from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('', views.home_view, name='home'), 
    path('search/', views.search, name='search'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('cart/remove/<int:product_id>/', views.cart_remove, name='cart_remove'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('my-orders/', views.my_orders_view, name='my_orders'),
    path('my-orders/<int:order_id>/', views.order_detail_view, name='order_detail'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('admin/orders/', views.admin_orders_view, name='admin_orders'),
    path('search/', views.search_view, name='search'),

]
