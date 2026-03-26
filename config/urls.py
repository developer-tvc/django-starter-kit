
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (SpectacularAPIView, SpectacularRedocView,
                                   SpectacularSwaggerView)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger'),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # Users
    path('api/v1/users/', include("apps.users.api.urls")),

    # Monitoring
    path('api/v1/monitoring/', include("apps.monitoring.api.urls"))
]
