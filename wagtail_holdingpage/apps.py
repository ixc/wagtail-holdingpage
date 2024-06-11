from django.apps import AppConfig
from django.conf import settings
from django.core.cache import cache
from django.db.models.signals import post_save


def clear_cache(sender, **kwargs):
    # Keep the check here, so we can override the setting during tests
    if getattr(settings, "HOLDINGPAGE_CLEAR_CACHE_ON_SAVE", False):
        cache.clear()


class WagtailHoldingpageAppConfig(AppConfig):
    name = "wagtail_holdingpage"
    ...

    def ready(self):
        post_save.connect(clear_cache, sender=self.get_model("HoldingPageSettings"))
