from django.urls import path
from . import views

urlpatterns = [
    path('chat/upload-image/', views.upload_image_chat, name='upload_image_chat'),
]
