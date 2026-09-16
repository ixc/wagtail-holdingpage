# Release process

We release from the `main` branch`:
- have the `main` branch pass CI
- advance the `[project]version` in the `pyproject.toml` to the new version, eg `version = "0.1.3"` and commit
- create a tag for the release, for example `v0.1.3`
- environment:
  * *do not* set `$UV_PUBLISH_USERNAME`, it inferferes with the token
  * set `$UV_PUBLISH_TOKEN` to the `ixc` account's API token for `wagtail-holdingpage`
- remove the `dist` subdirectory if it's present (we do not want to push up old stuff from it)
- `mkdir dist && uv build && uv publish`
- `git push --tags` to push the released tag up
- create a new release from github's code page for the new tag
