from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from django.utils.translation import gettext_lazy as _
from rest_framework.routers import DefaultRouter, SimpleRouter

from first_test.apps.people.views import MeViewSet

admin.site.site_title = _("first-test")
admin.site.site_header = _("first-test")


if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

router.register("me", MeViewSet, basename="me")

urlpatterns = [
    path("back/admin/", admin.site.urls),
    path("back/api/", include(router.urls)),
]

if settings.DEBUG:
    from drf_spectacular.views import (
        SpectacularAPIView,
        SpectacularRedocView,
        SpectacularSwaggerView,
    )

    urlpatterns = [
        path(
            "back/api/schema/",
            SpectacularAPIView.as_view(),
            name="schema",
        ),
        path(
            "back/api/schema/swagger-ui/",
            SpectacularSwaggerView.as_view(url_name="schema"),
            name="swagger-ui",
        ),
        path(
            "back/api/schema/redoc/",
            SpectacularRedocView.as_view(url_name="schema"),
            name="redoc",
        ),
    ] + urlpatterns