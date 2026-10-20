from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/consultations/$', consumers.ConsultationConsumer.as_asgi()),
    re_path(r'ws/medecin/$', consumers.MedecinConsumer.as_asgi()),
]
