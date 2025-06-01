from django.shortcuts import render, redirect
from .models import Product
from django.shortcuts import render, get_object_or_404
from django.shortcuts import get_object_or_404, redirect
from .cart import Cart
from .models import Product
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Order

def search(request):
    return render(request, 'app/search_results.html')


def home_view(request):
    return render(request, 'app/home.html')

@login_required
def my_orders_view(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'app/my_orders.html', {'orders': orders})

@login_required
def order_detail_view(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'app/order_detail.html', {'order': order})


def register_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('my_orders')
    else:
        form = UserCreationForm()
    return render(request, "app/register.html", {"form": form})

def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('my_orders')
        else:
            messages.error(request, "Tên đăng nhập hoặc mật khẩu không đúng")
    else:
        form = AuthenticationForm()
    return render(request, "app/login.html", {"form": form})

def logout_view(request):
    logout(request)
    return redirect('login')


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    flavors = product.flavor_options.split(",") if product.flavor_options else []
    weights = product.weight_options.split(",") if product.weight_options else []
    return render(request, 'app/detail.html', {
        'product': product,
        'flavors': flavors,
        'weights': weights,
    })

def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))
    cart.add(product, quantity)
    return redirect('cart_detail')

def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect('cart_detail')

def cart_detail(request):
    cart = Cart(request)
    return render(request, 'app/cart_detail.html', {'cart': cart})