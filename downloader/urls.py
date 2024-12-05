from django.urls import path
from .views import *
urlpatterns = [
    path('',home,name="home"),
     path('download/<str:video_id>/', download_video, name='download_video'),
     
]

