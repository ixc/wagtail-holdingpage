# wagtail-holdingpage

Proudly supported by the [Australian Museum](https://australian.museum/).

A widget for Wagtail's admin that gives you an admin interface to
control turning 'holding page mode' on and off for your website
while you deploy and test updates.

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

