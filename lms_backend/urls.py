from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("core.urls")),  # Frontend views (login, dashboard, etc.)
    path(
        "api-auth/", include("rest_framework.urls")
    ),  # Optional: DRF browsable login/logout
    path("ckeditor5/", include("django_ckeditor_5.urls")),  # CKEditor 5 URLs
]

# Serve media files during development (e.g., user avatars)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # Add debug toolbar URLs
    urlpatterns += [
        path("__debug__/", include("debug_toolbar.urls")),
    ]
