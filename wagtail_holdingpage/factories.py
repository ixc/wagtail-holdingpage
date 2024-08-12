from typing import Generic, TypeVar

from factory.base import FactoryMetaClass
from factory.django import DjangoModelFactory

from wagtail_holdingpage.models import HoldingPageAllowedPage, HoldingPageSettings

T = TypeVar("T")


class BaseMetaFactory(Generic[T], FactoryMetaClass):
    def __call__(cls, *args, **kwargs) -> T:
        return super().__call__(*args, **kwargs)


class HoldingPageSettingsFactory(
    DjangoModelFactory, metaclass=BaseMetaFactory[HoldingPageSettings]
):
    class Meta:
        model = HoldingPageSettings


class HoldingPageAllowedPageFactory(
    DjangoModelFactory, metaclass=BaseMetaFactory[HoldingPageAllowedPage]
):
    class Meta:
        model = HoldingPageAllowedPage
