# Release process

We release from the `main` branch`:
- have the `main` branch pass CI
- advance the `[project]version` in the `pyproject.toml` to the new version, eg `version = "0.1.3"` and commit
- create a tag for the release, for example `v0.1.3`
- put the `ixc` accounts API token for `wagtail-holdingpage` into the `$UV_PUBLISH_TOKEN` environment variable
- remove out the `dist` subdirectory if it's present
- `mkdir dist && uv build && uv publish`
- `git push --tags` to push the released tag up
