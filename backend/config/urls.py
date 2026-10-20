from django.contrib import admin
from django.urls import path, include
from apps.messaging.media import private_media

urlpatterns = [
    path('media/<path:path>', private_media, name='private_media'),
    path('django-admin/', admin.site.urls),
    path('', include('apps.accounts.urls')),
    path('patients/', include('apps.patients.urls')),
    path('', include('apps.consultations.urls')),
    path('api/sensors/', include('apps.sensors.urls')),
    path('', include('apps.ordonnances.urls')),
    path('api/', include('apps.messaging.urls')),
]
