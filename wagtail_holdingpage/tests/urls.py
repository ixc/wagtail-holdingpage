from django.urls import include, path, re_path
from wagtail import urls as wagtail_urls

from wagtail_holdingpage.tests.testapp import views

urlpatterns = [
    path("", views.index),
    re_path(r"^a_path/", views.a_view),
    re_path(r"^another_path/", views.another_view),
    re_path(r"^another_path/folder/", views.index),
    re_path(r"^decorated/", views.decorated_view),
    re_path(r"^not_decorated/", views.not_decorated_view),
    re_path(r"^a_view/", views.a_view),
    re_path(r"^another_view/", views.another_view),
    path("", include(wagtail_urls)),
]
