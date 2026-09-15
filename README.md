# wagtail-holdingpage

Proudly supported by the [Australian Museum](https://australian.museum/).

A widget for Wagtail's admin that gives you an admin interface to
control turning 'holding page mode' on and off for your website
while you deploy and test updates.

When 'holding page mode' is on, visitors will see the holding page template instead of the normal site content, and the response code will be `503 Service Unavailable`. Holding page responses are decorated with Django's `never_cache` decorator.

## Use

When holding page mode is on, it will display a nice-looking
maintenance page, but optionally allow some pages to behave as
normal, or allow the site to behave as normal for admins. In your
settings you can exclude certain URLs (eg `/admin`) from being affected.

<img width="1103" height="1091" alt="Image" src="https://github.com/user-attachments/assets/c8b3bb09-91fd-498b-a74e-141de692bccd" />

## Installation

```
python3 -m pip install wagtail-holdingpage
```

Add `"wagtail_holdingpage.apps.WagtailHoldingpageAppConfig"` to `INSTALLED_APPS`.

Add `"wagtail_holdingpage.middleware.HoldingPageMiddleware"` to `MIDDLEWARE`, normally _below_ any session and authentication middleware.

Set `HOLDINGPAGE_TEMPLATE_NAME` in your Django settings to the path of the template you want to use for the holding page. Alternatively, override the default template "wagtail_holdingpage/holding_page.html".

Optionally, add the following settings to your settings file, for example:

```python
HOLDINGPAGE_ALLOWED_URL_PATTERNS = [
    "^/admin/*",
    "^/robots.txt",
    "/favicon.ico",
]
```

Optionally, create additional hooks to allow certain requests to bypass the holding page. See `hooks.py` for an example. `HoldingpageSettings` allows you to control whether the `allow_staff` hook is enabled via the Wagtail admin. Alternatively, you can configure it to be always enabled via `HOLDINGPAGE_HOOKS` (overrides the admin setting).

```python
HOLDINGPAGE_HOOKS = [
    "myapp.hooks.my_hook",
]
```

Optionally, set `HOLDINGPAGE_REDIRECT_URL` in your Django settings to specify a URL to which visitors should be 302 redirected when the holding page is active. This can be useful if the holding page is external, but note that visitors may remain on that redirect destination and simply refresh it and so they'll never know when holding page mode is turned off. You might want to redirect them back to the main site once the holding page mode is turned off.

```python
HOLDINGPAGE_REDIRECT_URL = "https://otherdomain.com/maintenance/"
```
