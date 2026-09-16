# Release process

We release from the `main` branch`:
- have the `main` branch pass CI
- create a tag for the release, for example `v0.1.3`
- put the `ixc` accounts API token for `wagtail-holdingpage` into the `$UV_PUBLISH_TOKEN` environment variable
- remove out the `dist` subdirectory if it's present
- `mkdir dist && uv build && uv publish`
- `git push` to push the released tag up
