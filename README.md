# LenBot 插件模板

[English](README.en.md)

一个能直接运行的计数插件，用来起步写自己的 LenBot 插件。

## 开始

1. 在 GitHub 上点 Use this template 生成自己的仓库。
2. 改 `plugin.toml` 里的 `name`、`authors`、`version` 和 `license`。
3. 把命令和工具改成自己的名字，避免和别的插件重名。

## 示例做了什么

- `/计数`：读当前群的计数。
- `计数加一`：按配置里的 `step` 增加。
- `/计数清零`：清零。
- 工具 `counter_read`：返回当前群的计数 JSON，不发消息。
- 工具 `counter_card`：后台生成计数说明后自行发送；需要宿主配置模型。

计数按群分开存，更新插件源码不会清掉。

## 测试

```sh
uv run --no-sync pytest -q tests
```

测试用宿主提供的 `PluginTest` 模拟消息和配置，不用启动 LenBot。CI 会安装 `.github/workflows/ci.yml` 里固定的宿主版本再跑测试，升级宿主时改这个版本。

## 发布

1. 改 `plugin.toml` 的版本号并提交。
2. 打 `v*` 标签，工作流会生成 ZIP 并挂到 GitHub Release。

用户可以在面板里填仓库地址用 Git 安装，也可以导入 Release 里的 ZIP。配置或数据格式有变化时写在 README 里；回退源码不会回退已经存下的数据。

接口、生命周期和配置说明见宿主仓库的 `developer/plugins-v1.md`。

## 许可证

模板采用 [GPL-3.0-only](LICENSE)。LenBot 宿主采用 AGPL-3.0-only，插件和宿主运行在同一个进程里，推荐插件也使用 GPL-3.0；改用其他许可证前请确认它与 GPLv3／AGPLv3 兼容。

## 工具接口

工具采用接口 1 的显式简介、Field 参数说明与 `prompts/tools.md` 共享指南，返回原生 JSON 或文本。用 `PluginTest.preview_tools()` 查看模型说明、参数与可用性；模型服务默认关闭，真实发送仍单独核对。兼容和更新事项见 [CHANGELOG](CHANGELOG.md)。

CI 固定到包含当前插件接口的宿主开发提交；本次未创建版本标签或 Release。catalog-entry.json 只记录开发安装来源，未公开插件不加入主目录。

本机生成 ZIP：`uv run --no-project --python 3.13 python scripts/package.py /tmp/plugin.zip`。打包取 Git 已跟踪的运行源码和资源，新增文件需先加入 Git；不会收录本机环境、测试或配置。

## 工具数量与能力边界

本模板保留两个工具：counter_read 查询 JSON；counter_card 开始后台生成并自行发送。两种结果语义不同，所以分别暴露。不要为每个 HTTP 端点、列表页、详情页或随机选项再加一个工具。

同一能力需要多种操作时，可用 `request: Annotated[SearchRequest | ReadRequest, Field(discriminator="action")]`；各 Request 继承配置 `ConfigDict(strict=True, extra="forbid")` 的 BaseModel，并分别声明 `action: Literal["search"]`／`Literal["read"]` 和所需字段。列表、详情使用同一工具；查询和真实发送／账号写入保持清楚的边界。不要堆一组互斥可选参数。

用 PluginTest.preview_tools() 核对实际工具数、发现目录、共享指南与每个操作的 schema。工具数量减少不等于 schema 一定减少，检查目录和真实加载内容；已有生成 title 在模型参数中去掉，Field 的说明、示例和约束保留。
