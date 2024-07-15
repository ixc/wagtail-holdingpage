from django.conf import settings
from django.http import HttpResponseRedirect
from django.urls import NoReverseMatch, Resolver404, get_resolver
from wagtail.models import Site

from wagtail_holdingpage.hooks import allow_staff
from wagtail_holdingpage.models import HoldingPageSettings
from wagtail_holdingpage.views import UncachedTemplateView


class HoldingPageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        site = Site.find_for_request(request)
        self.holdingpage_settings = HoldingPageSettings.for_site(site=site)

        return self.get_response(request)

    def _matches_allowed_view(self, view):
        from wagtail_holdingpage import holdingpage_registry

        if holdingpage_registry.allowed_views:
            for allowed_view in holdingpage_registry.allowed_views:
                if view == allowed_view:
                    return True
        return False

    def _matches_allowed_path(self, path):
        from wagtail_holdingpage import holdingpage_registry

        if holdingpage_registry.allowed_url_patterns:
            for pattern in holdingpage_registry.allowed_url_patterns:
                if pattern.match(path) is not None:
                    return True
        for pattern in self.holdingpage_settings.allowed_url_regexes():
            if pattern.match(path) is not None:
                return True
        return False

    def process_view(self, request, view_func, view_args, view_kwargs):
        from wagtail_holdingpage import holdingpage_registry
        from wagtail_holdingpage.decorators import AllowedView

        # Allow access if middleware is not activated
        if not self.holdingpage_settings.holdingpage_active:
            return None

        # Allow overriding the HOLDINGPAGE_HOOKS setting via the Wagtail setting
        hooks = holdingpage_registry.hooks
        if self.holdingpage_settings.allow_staff and allow_staff not in hooks:
            hooks.append(allow_staff)

        # Allow access if one of the hooks returns True
        for hook in holdingpage_registry.hooks:
            if hook(request):
                return None

        # See if the path matches a view
        try:
            view_func = get_resolver(None).resolve(request.get_full_path())[0]

            # Allow access if the view was decorated with the allowed_view decorator
            if isinstance(view_func, AllowedView):
                return None

            # Allow access if view is explicity allowed in settings
            if self._matches_allowed_view(view_func):
                return None

            # Allow access to allowed views, doh!
            if view_func in holdingpage_registry.allowed_views:
                return None

        except (NoReverseMatch, Resolver404):
            pass

        # Allow access if path is explicity allowed in settings
        if self._matches_allowed_path(request.path):
            return None

        # We should present the holding page, either by redirecting, or
        # via a template view.

        holdingpage_redirect_url = holdingpage_registry.holdingpage_url

        if (
            holdingpage_redirect_url
            and holdingpage_redirect_url != request.get_full_path()
        ):
            # Redirect to holding page if required, unless we're already on the holdingpage
            return HttpResponseRedirect(holdingpage_redirect_url)

        # Render holding page template view
        template_name = getattr(
            settings,
            "HOLDINGPAGE_TEMPLATE_NAME",
            "wagtail_holdingpage/holdingpage.html",
        )
        return UncachedTemplateView.as_view(template_name=template_name)(request)
