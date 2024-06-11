import re
from http import HTTPStatus

import wagtail_factories
from ddt import data, ddt
from django.conf import settings
from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.management import call_command
from django.test import TestCase, override_settings
from wagtail.core.models import Page, Site

from wagtail_holdingpage import holdingpage_registry
from wagtail_holdingpage.factories import (HoldingPageAllowedPageFactory,
                                           HoldingPageSettingsFactory)
from wagtail_holdingpage.hooks import allow_staff
from wagtail_holdingpage.tests.testapp.views import another_view


class HoldingPageTestMixin:
    def setUp(self):
        super().setUp()
        self.staff_user = SuperAdminFactory.create()
        self.notstaff_user = UserFactory.create()
        holdingpage_registry.load_settings()

        Site.objects.all().delete()
        Page.objects.all().delete()

        self.root_page = RootPageFactory.create()
        self.home_page = AmHomePageFactory(parent=self.root_page, title="Homepage")
        self.site = wagtail_factories.SiteFactory(
            site_name="Example Site",
            root_page=self.home_page,
            is_default_site=True,  # important
            port=8000,
        )

    # Util functions --------------------------------------------------------

    def assertHoldingPageRedirect(self, url):
        # Should render the holding page template, for any url.
        response = self.client.get(url, follow=True)
        holdingpage_url = getattr(settings, "HOLDINGPAGE_URL", None)
        self.assertEquals(response.redirect_chain, [(holdingpage_url, 302)])
        self.assertContains(
            response,
            text="This is a holding page",
            count=1,
            status_code=HTTPStatus.SERVICE_UNAVAILABLE,
        )
        return response

    def assertHoldingPageRender(self, url):
        # Should render the holding page template, for any url.
        response = self.client.get(url, follow=True)
        self.assertTemplateUsed(response, "wagtail_holdingpage/holdingpage.html")
        self.assertEqual(response.status_code, HTTPStatus.SERVICE_UNAVAILABLE)
        return response

    def assertHoldingPage(self, url, holdingpage_url):
        if holdingpage_url:
            return self.assertHoldingPageRedirect(url)
        return self.assertHoldingPageRender(url)

    def assertNormalPage(self, url):
        response = self.client.get(url)
        self.assertContains(
            response, text="Normal page", count=1, status_code=HTTPStatus.OK
        )
        return response


@ddt
@override_settings(
    ROOT_URLCONF="wagtail_holdingpage.tests.urls",
    INSTALLED_APPS=settings.INSTALLED_APPS + ["wagtail_holdingpage.tests.testapp"],
    HOLDINGPAGE_ALLOWED_VIEWS=["wagtail_holdingpage.tests.testapp.views.a_view"],
    HOLDINGPAGE_TEMPLATE_NAME="wagtail_holdingpage/holdingpage.html",
)
class HoldingPageMiddlewareTestCase(HoldingPageTestMixin, TestCase):
    def tearDown(self):
        super().tearDown()
        cache.clear()

    # Actual tests --------------------------------------------------------

    def test_disabled_middleware(self):
        "Explicitly disabling the holdingpage_activated setting should work"
        HoldingPageSettingsFactory(site=self.site, holdingpage_active=False)
        holdingpage_registry.load_settings()
        self.assertNormalPage("/")

    @data(
        None,
        "/holding-test/",
    )
    def test_enabled_middleware(self, holdingpage_url):
        HoldingPageSettingsFactory(site=self.site, holdingpage_active=True)
        with override_settings(HOLDINGPAGE_URL=holdingpage_url):
            holdingpage_registry.load_settings()
            self.assertHoldingPage("/", holdingpage_url)

    @data(
        None,
        "/holding-test/",
    )
    def test_holdingpage_not_cached(self, holdingpage_url):
        HoldingPageSettingsFactory(site=self.site, holdingpage_active=True)
        with override_settings(
            HOLDINGPAGE_URL=holdingpage_url,
            MIDDLEWARE=settings.PUBLIC_SITE_MIDDLEWARE,
        ):
            holdingpage_registry.load_settings()
            response = self.assertHoldingPage("/", holdingpage_url)
            self.assertEqual(
                response["Cache-Control"],
                "max-age=0, no-cache, no-store, must-revalidate, private",
            )

    @data(
        None,
        "/holding-test/",
    )
    def test_without_view_hooks(self, holdingpage_url):
        HoldingPageSettingsFactory(site=self.site, holdingpage_active=True)
        with override_settings(
            HOLDINGPAGE_HOOKS=[],
            HOLDINGPAGE_URL=holdingpage_url,
            IS_ADMIN_SITE=True,
        ):
            holdingpage_registry.load_settings()
            self.client.force_login(user=self.notstaff_user)
            self.assertHoldingPage("/", holdingpage_url)
            self.client.force_login(user=self.staff_user)
            self.assertHoldingPage("/", holdingpage_url)

    @data(
        None,
        "/holding-test/",
    )
    def test_with_view_hooks(self, holdingpage_url):
        HoldingPageSettingsFactory(site=self.site, holdingpage_active=True)
        with override_settings(
            HOLDINGPAGE_HOOKS=["wagtail_holdingpage.hooks.allow_staff"],
            HOLDINGPAGE_URL=holdingpage_url,
            IS_ADMIN_SITE=True,
        ):
            holdingpage_registry.load_settings()
            self.client.force_login(user=self.notstaff_user)
            self.assertHoldingPage("/", holdingpage_url)
            self.client.force_login(user=self.staff_user)
            self.assertNormalPage("/")

    @data(
        None,
        "/holding-test/",
    )
    def test_allowed_paths(self, holdingpage_url):
        HoldingPageSettingsFactory(site=self.site, holdingpage_active=True)
        with override_settings(
            HOLDINGPAGE_URL=holdingpage_url,
        ):
            holdingpage_registry.load_settings()
            old_paths = holdingpage_registry.allowed_url_patterns  # Back up old paths
            self.assertNormalPage("/a_path/")  # Explicitly allowed in setUp above
            self.assertHoldingPage("/another_path/", holdingpage_url)

            holdingpage_registry.allowed_url_patterns = old_paths + [
                re.compile("^/another_path/$")
            ]
            self.assertNormalPage("/another_path/")
            self.assertHoldingPage("/another_path/folder/", holdingpage_url)

            holdingpage_registry.allowed_url_patterns = old_paths + [
                re.compile("^/another_path(.*)$")
            ]
            self.assertNormalPage("/another_path/")
            self.assertNormalPage("/another_path/folder/")

            holdingpage_registry.allowed_url_patterns = old_paths  # Restore old paths

    @data(
        None,
        "/holding-test/",
    )
    def test_decorated_views(self, holdingpage_url):
        HoldingPageSettingsFactory(site=self.site, holdingpage_active=True)
        with override_settings(
            HOLDINGPAGE_URL=holdingpage_url,
        ):
            holdingpage_registry.load_settings()
            self.assertNormalPage("/decorated/")
            self.assertHoldingPage("/not_decorated/", holdingpage_url)

    @data(
        None,
        "/holding-test/",
    )
    def test_allowed_views(self, holdingpage_url):
        HoldingPageSettingsFactory(site=self.site, holdingpage_active=True)
        with override_settings(
            HOLDINGPAGE_URL=holdingpage_url,
        ):
            holdingpage_registry.load_settings()
            old_views = holdingpage_registry.allowed_views  # Back up old views
            self.assertNormalPage("/a_view/")  # Explicitly allowed in setUp above
            self.assertHoldingPage("/another_view/", holdingpage_url)

            holdingpage_registry.allowed_views = old_views + [another_view]
            self.assertNormalPage("/a_view/")
            self.assertNormalPage("/another_view/")

            holdingpage_registry.allowed_views = old_views  # Restore old paths


@ddt
@override_settings(
    ROOT_URLCONF="wagtail_holdingpage.tests.urls",
    INSTALLED_APPS=settings.INSTALLED_APPS + ["wagtail_holdingpage.tests.testapp"],
    HOLDINGPAGE_ALLOWED_VIEWS=["wagtail_holdingpage.tests.testapp.views.a_view"],
    HOLDINGPAGE_TEMPLATE_NAME="wagtail_holdingpage/holdingpage.html",
)
class SettingsTest(HoldingPageTestMixin, AdminTest):
    def setUp(self):
        super().setUp()
        self.model_path = "settings/wagtail_holdingpage/holdingpagesettings/"  # example: "page/" or "pages/basicpage/

    def get_edit_instance_path(self, instance):
        """example: /admin/settings/wagtail_holdingpage/holdingpagesettings/888/"""
        return "{admin_path}{model_path}{site_id}/".format(
            admin_path=self.admin_path,
            model_path=self.model_path,
            site_id=instance.site_id,
        )

    @data(
        True,
        False,
    )
    def test_holding_page_active(self, holdingpage_active):
        settings = HoldingPageSettingsFactory(
            site=self.site, holdingpage_active=holdingpage_active
        )
        holdingpage_registry.load_settings()
        if holdingpage_active:
            self.assertHoldingPage("/", holdingpage_url=None)
        else:
            self.assertNormalPage("/")

    @data(
        True,
        False,
    )
    def test_allow_staff(self, allow_staff):
        settings = HoldingPageSettingsFactory(
            site=self.site, holdingpage_active=True, allow_staff=allow_staff
        )
        holdingpage_registry.load_settings()
        if allow_staff:
            self.client.force_login(self.notstaff_user)
            self.assertHoldingPage("/", holdingpage_url=None)
            self.client.force_login(self.staff_user)
            self.assertNormalPage("/")
        else:
            self.client.force_login(self.notstaff_user)
            self.assertHoldingPage("/", holdingpage_url=None)
            self.client.force_login(self.staff_user)
            self.assertHoldingPage("/", holdingpage_url=None)

    @data(
        True,
        False,
    )
    def test_cache_cleared_on_settings_change(self, clear_cache):
        settings = HoldingPageSettingsFactory(site=self.site, holdingpage_active=True)
        with override_settings(HOLDINGPAGE_CLEAR_CACHE_ON_SAVE=clear_cache):
            cache.set("test", "test", 100)
            self.assertEqual(cache.get("test"), "test")
            settings.holdingpage_active = False
            settings.save()
            self.assertEqual(bool(cache.get("test")), not clear_cache)

    @override_settings(IS_ADMIN_SITE=True)
    def test_settings__can_edit(self):
        settings = HoldingPageSettingsFactory(site=self.site, holdingpage_active=False)
        response, form = self.get_edit_instance_as_admin(
            instance=settings, admin=self.staff_user
        )
        self.assertEqual(response.status_code, 200)

    @override_settings(IS_ADMIN_SITE=True)
    def test_settings__can_allow_pages(self):
        settings = HoldingPageSettingsFactory(site=self.site, holdingpage_active=False)
        response, form = self.get_edit_instance_as_admin(
            instance=settings, admin=self.staff_user
        )
        self.assertTrue("holdingpage_allowed_pages-TOTAL_FORMS" in form.fields.keys())

    @data(True, False)
    @override_settings(IS_ADMIN_SITE=True)
    def test_settings__can_allow_pages(self, include_descendants):
        settings = HoldingPageSettingsFactory(site=self.site, holdingpage_active=False)
        allowed_page = HoldingPageAllowedPageFactory(
            settings=settings,
            page=self.home_page,
            include_descendants=include_descendants,
        )
        expected_url = (
            re.compile(f"^/")
            if include_descendants
            else re.compile(f"^/$")
        )
        self.assertTrue(expected_url in settings.allowed_url_regexes())

    @data(True, False)
    @override_settings(IS_ADMIN_SITE=True)
    def test_settings__allowed_pages_are_accessible(self, include_descendants):
        settings = HoldingPageSettingsFactory(site=self.site, holdingpage_active=True)
        allowed_child = BasicPageFactory(parent=self.home_page)
        allowed_grandchild = BasicPageFactory(parent=allowed_child)
        HoldingPageAllowedPageFactory(
            settings=settings,
            page=allowed_child,
            include_descendants=include_descendants,
        )
        # Ensure not logged in
        self.client.logout()
        self.assert_page_loading(
            path=allowed_child.url,
            status_code=HTTPStatus.OK,
        )
        grandchild_status = (
            HTTPStatus.OK if include_descendants else HTTPStatus.SERVICE_UNAVAILABLE
        )
        self.assert_page_loading(
            path=allowed_grandchild.url,
            status_code=grandchild_status,
        )
        self.assert_page_loading(
            path="/",
            status_code=HTTPStatus.SERVICE_UNAVAILABLE,
        )
