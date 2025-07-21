from django.urls import path
from .views import *

urlpatterns = [
    path('create_s_url/', CreateShortUrl.as_view(), name='create_shorturl'),
    path('shorturl/<str:shortcode>/', CreateShortUrl.as_view(), name='stats_shorturl'),
    path('r/<str:code>/', redirect_url, name='redirect_shorturl'),
]