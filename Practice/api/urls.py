from django.urls import path
from . import views

urlpatterns = [
    path('', views.api_home),
    path('product/', views.api_product),
    path('ProForm/', views.api_product_form),
    path('api_rest/', views.api_rest),
    path('serial/', views.api_rest_serializer),
    path('post/', views.api_post_data),
]