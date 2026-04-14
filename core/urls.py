from django.contrib import admin
from django.urls import include, path

from django.conf import settings
from django.conf.urls.static import static
from pathlib import Path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("apps.content.urls")),
    path("accounts/", include("apps.accounts.urls")),
    path("tinymce/", include("tinymce.urls")),

]

# == Debug Endpoints (only available in DEBUG mode) ==>

# health check views
from core.settings.development.health import health_check, ready_check, live_check
# diagnostic views
from core.settings.development.diagnostics import static_files_debug, system_info

if settings.DEBUG:
    urlpatterns += [
        path("debug/static/", static_files_debug, name="static-debug"),
        path("debug/system/", system_info, name="system-debug"),
        # == Health Check Endpoints ==>
        path("health/", health_check, name="health-check"),
        path("ready/", ready_check, name="ready-check"), 
        path("live/", live_check, name="live-check"),
        

    ]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Debug toolbar URLs
if settings.DEBUG and getattr(settings, 'ENABLE_DEBUG_TOOLBAR', False):
    try:
        import debug_toolbar

        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns
    except ImportError:
        pass