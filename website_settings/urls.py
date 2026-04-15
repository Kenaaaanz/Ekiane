from django.urls import path
from . import views

app_name = 'website_settings'

urlpatterns = [
    path('', views.website_settings, name='settings'),
]