# LenBot plugin template

[中文](README.md)

A working counter plugin to start your own LenBot plugin from.

## Getting started

1. Click Use this template on GitHub to create your repository.
2. Change `name`, `authors`, `version` and `license` in `plugin.toml`.
3. Rename the commands and tools so they don't collide with other plugins.

## What the example does

- `/计数` reads the count for the current group.
- `计数加一` adds the configured `step`.
- `/计数清零` resets it.
- The `counter_read` tool returns the current count as JSON.

Counts are stored per group and survive source updates.

## Testing

```sh
uv run --no-sync pytest -q tests
```

Tests use the host's `PluginTest` harness to simulate messages and configuration, so they run directly in this repository. CI calls LenBot's reusable workflow, which tests and packages the plugin against host `master` by default; pass `host_ref` in `.github/workflows/ci.yml` to pin a host version.

## Releasing

1. Bump the version in `plugin.toml` and commit.
2. Push a `v*` tag. The workflow builds a ZIP and attaches it to a GitHub Release.

Users can install from the repository URL with Git in the panel, or import the ZIP from the Release. Document configuration or data format changes in the README; stored data stays as it is when source is rolled back.

See `developer/plugins-v1.en.md` in the host repository for the interface, lifecycle and configuration.

## License

The template is [GPL-3.0-only](LICENSE). The LenBot host is AGPL-3.0-only and plugins run in the host process, so GPL-3.0 is the recommended plugin license; if you choose another license, check its compatibility with GPLv3 and AGPLv3.

Tool interface 1 now uses explicit discovery summaries, shared `prompts/tools.md` instructions and native JSON results. `counter_read` returns data; `counter_card` starts background model generation and sends the completed text itself. Use `PluginTest.preview_tools()` to inspect the actual schemas. Tests call a model only when `models=` is provided. See CHANGELOG.md for the final 0.2.0 host baseline requirement.

Group tools by user capability rather than HTTP endpoint. Keep data lookup and actual delivery separate. Use a discriminated request union for related search/detail operations, with strict models forbidding unrelated fields. Inspect both the discovery catalog and loaded schema, and check tool count and schema size separately. This template retains two useful capabilities.
