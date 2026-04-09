from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('productbatch/', views.productbatch_list, name='productbatch_list'),
    path('api/productbatch/', views.productbatch_api, name='productbatch_api'),
    path('api/analytics/', views.analytics_api, name='analytics_api'),
]