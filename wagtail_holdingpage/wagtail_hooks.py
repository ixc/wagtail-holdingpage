from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from wagtail import hooks
from wagtail.admin.menu import MenuItem

from australian_museum.common.constants import SETTINGS_MENU_ORDER__HOLDING_PAGE


@hooks.register("register_settings_menu_item")
def register_holding_page_settings():
    return MenuItem(
        _("Holding Page Settings"),
        reverse(
            "wagtailsettings:edit", args=("wagtail_holdingpage", "holdingpagesettings")
        ),
        classname="icon icon-cog",
        order=SETTINGS_MENU_ORDER__HOLDING_PAGE,
    )
