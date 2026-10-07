"""Run the example through the public local plugin harness."""

import json
from pathlib import Path

import pytest

from len_bot.plugin_testing import PluginTest


@pytest.mark.asyncio
async def test_counter_keeps_scenes_separate_and_uses_saved_step():
    scenes = ('onebot:group:80001', 'onebot:group:80002')
    async with PluginTest(Path(__file__).parents[1], config={'step': 2}, scenes=scenes) as bot:
        assert await bot.message('计数加一', scene=scenes[0])
        assert bot.deliveries[-1].text == '本群计数：2'
        assert bot.deliveries[-1].status == 'simulated'
        assert json.loads(await bot.tool('counter_read', {}, scene=scenes[1]))['count'] == 0
        assert await bot.message('/计数清零', scene=scenes[0])
        assert json.loads(await bot.tool('counter_read', {}, scene=scenes[0]))['count'] == 0


@pytest.mark.asyncio
async def test_background_generation_uses_explicit_model_protocol_and_simulated_send():
    import asyncio
    import re
    calls = []

    async def respond(reader, writer):
        headers = await reader.readuntil(b'\r\n\r\n')
        length = int(re.search(rb'content-length:\s*(\d+)', headers, re.I)[1])
        request = json.loads(await reader.readexactly(length))
        calls.append(request)
        body = json.dumps({'id': 'synthetic', 'object': 'chat.completion', 'created': 1234567890,
            'model': 'local', 'choices': [{'index': 0, 'message': {'role': 'assistant',
            'content': '当前计数为 2。'}, 'finish_reason': 'stop'}],
            'usage': {'prompt_tokens': 20, 'completion_tokens': 10, 'total_tokens': 30}}).encode()
        writer.write(b'HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: '
                     + str(len(body)).encode() + b'\r\nConnection: close\r\n\r\n' + body)
        await writer.drain()
        writer.close()
        await writer.wait_closed()

    server = await asyncio.start_server(respond, '127.0.0.1', 0)
    url = f'http://127.0.0.1:{server.sockets[0].getsockname()[1]}/v1'
    models = {'providers': {'local': {'api': 'openai-chat', 'base_url': url, 'api_key': 'synthetic'}},
              'roles': {'mind': {'provider': 'local', 'model': 'local', 'context_window_tokens': 8192}}}
    async with server, PluginTest(Path(__file__).parents[1], config={'step': 2},
                                  now=lambda: 1234567890, models=models) as bot:
        preview = {item['name']: item for item in bot.preview_tools()}
        assert {'counter_read', 'counter_card'} == preview.keys()
        assert all(item['summary'] and item['instructions'] for item in preview.values())
        await bot.message('计数加一')
        result = json.loads(await bot.tool('counter_card', {}))
        assert result == {'status': 'started', 'delivery': 'plugin', 'count': 2}
        await bot.wait_tasks('counter-card')
        assert len(calls) == 1 and '2' in calls[0]['messages'][-1]['content']
        assert bot.deliveries[-1].text == '当前计数为 2。'
        assert bot.deliveries[-1].status == 'simulated'
        assert bot.events()
