from django.urls import path
from . import views

urlpatterns = [
    # path('<int:pk>', views.ProductDetailAPIView.as_view()),
    # path('', views.product_create_view),
    # path('<int:pk>/', views.product_detail_view),
    # path('', views.product_alt_view),
    # path('', views.product_mixin_view),
    # path('<int:pk>/', views.product_mixin_view),
    path('', views.product_list_create_mixin_view),
    path('<int:pk>/', views.product_list_create_mixin_view),
    path('<int:pk>/update/', views.product_update_view),
    path('<int:pk>/delete/', views.product_destroy_view),

]