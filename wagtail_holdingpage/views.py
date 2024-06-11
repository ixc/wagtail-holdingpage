from http import HTTPStatus

from django.template.response import TemplateResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.generic import TemplateView


class TemplateResponseUnavailable(TemplateResponse):
    status_code = HTTPStatus.SERVICE_UNAVAILABLE


@method_decorator(never_cache, name="dispatch")
class UncachedTemplateView(TemplateView):
    """Subclassed to add the decorator, and the response code"""

    response_class = TemplateResponseUnavailable
