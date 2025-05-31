from django.shortcuts import render
from .models import Product
from django.shortcuts import render, get_object_or_404
from django.shortcuts import get_object_or_404, redirect
from .cart import Cart
from .models import Product
def home(request):
    products = Product.objects.all()
    return render(request, 'app/home.html', {'products': products})

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