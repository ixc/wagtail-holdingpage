from django.conf.urls import include, url
from wagtail.core import urls as wagtail_urls

from wagtail_holdingpage.tests.testapp import views

urlpatterns = [
    url(r"^$", views.index),
    url(r"^a_path/", views.a_view),
    url(r"^another_path/", views.another_view),
    url(r"^another_path/folder/", views.index),
    url(r"^decorated/", views.decorated_view),
    url(r"^not_decorated/", views.not_decorated_view),
    url(r"^a_view/", views.a_view),
    url(r"^another_view/", views.another_view),
    url(r"", include(wagtail_urls)),
]
