import re

from django.db import models
from django.utils.translation import gettext_lazy as _
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.contrib.settings.models import BaseSiteSetting
from wagtail.contrib.settings.registry import register_setting


class HoldingPageAllowedPage(models.Model):
    page = models.ForeignKey(
        "wagtailcore.Page",
        on_delete=models.CASCADE,
        help_text=_(
            "Select a page whose content should be visible, "
            "even when the holding page is activated."
        ),
    )
    settings = ParentalKey(
        "HoldingPageSettings",
        related_name="allowed_pages",
        on_delete=models.PROTECT,
    )
    include_descendants = models.BooleanField(
        default=False,
        help_text=_(
            "Check this box to make the decsendants of "
            "the selected page visible as well."
        ),
    )

    panels = [
        FieldPanel("page"),
        FieldPanel("include_descendants"),
    ]

    def __str__(self):
        return f"{self.page} allowed for {self.settings}"


@register_setting
class HoldingPageSettings(ClusterableModel, BaseSiteSetting):
    """Settings for HoldingPage mode"""

    holdingpage_active = models.BooleanField(
        default=False, help_text="Enable holding page"
    )
    allow_staff = models.BooleanField(
        default=False,
        help_text="Allow staff to access the site, even with holding page enadled",
    )

    panels = [
        FieldPanel("holdingpage_active"),
        FieldPanel("allow_staff"),
        InlinePanel(
            relation_name="allowed_pages",
            heading="Allowed Pages",
            label="Allowed Page",
        ),
    ]

    def allowed_url_regexes(self):
        """
        Get the list of page regexes for matching against an incoming request
        """

        regexes = []
        for allowed_page in self.allowed_pages.all():
            _, _, page_path = allowed_page.page.get_url_parts()
            if allowed_page.include_descendants:
                regexes.append(re.compile(rf"^{page_path}"))
            else:
                regexes.append(re.compile(rf"^{page_path}$"))

        return regexes
