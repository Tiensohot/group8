from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('', views.home_view, name='home'), 
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('cart/remove/<int:product_id>/', views.cart_remove, name='cart_remove'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('my-orders/', views.my_orders_view, name='my_orders'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('admin/orders/', views.admin_orders_view, name='admin_orders'),
    path('search/', views.search_view, name='search'),
    path('shop/', views.product_list_view, name='product_list'),
    path('blog/', views.blog_view, name='blog'),
    path('blog/<int:post_id>/', views.blog_detail_view, name='blog_detail'),
    path('payment/momo/<int:order_id>/', views.momo_payment_view, name='momo_payment'),
    path('order/<int:order_id>/', views.order_detail_view, name='order_detail'),
]
