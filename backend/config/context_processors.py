from django.conf import settings


def webrtc(request):
    return {'webrtc_ice_servers': settings.WEBRTC_ICE_SERVERS}
