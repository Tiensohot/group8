from django.shortcuts import render, redirect
from .models import Product
from django.shortcuts import render, get_object_or_404
from django.shortcuts import get_object_or_404, redirect
from .cart import Cart
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Order
from .form import CheckoutForm
from .models import Order, OrderItem
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
import random
from .models import Product, Review
from django.urls import reverse #dong xung dot


import requests
import json
from django.shortcuts import redirect
from django.conf import settings

def momo_payment_view(request, order_id):
    order = Order.objects.get(id=order_id, user=request.user)
    endpoint = "https://test-payment.momo.vn/v2/gateway/api/create"
    partnerCode = settings.MOMO_PARTNER_CODE
    accessKey = settings.MOMO_ACCESS_KEY
    secretKey = settings.MOMO_SECRET_KEY
    returnUrl = request.build_absolute_uri('/momo_return/')
    notifyUrl = request.build_absolute_uri('/momo_notify/')

    requestId = str(order.id)
    amount = str(int(order.total_price))
    orderInfo = "Thanh toán đơn hàng #" + str(order.id)
    extraData = ""

    raw_signature = f"accessKey={accessKey}&amount={amount}&extraData={extraData}&ipnUrl={notifyUrl}&orderId={requestId}&orderInfo={orderInfo}&partnerCode={partnerCode}&redirectUrl={returnUrl}&requestId={requestId}&requestType=captureWallet"
    # tạo chữ ký bằng HMAC SHA256 theo secretKey (đoạn này bạn cần dùng thư viện hmac)
    import hmac, hashlib
    signature = hmac.new(secretKey.encode(), raw_signature.encode(), hashlib.sha256).hexdigest()

    data = {
        "partnerCode": partnerCode,
        "accessKey": accessKey,
        "requestId": requestId,
        "amount": amount,
        "orderId": requestId,
        "orderInfo": orderInfo,
        "redirectUrl": returnUrl,
        "ipnUrl": notifyUrl,
        "extraData": extraData,
        "requestType": "captureWallet",
        "signature": signature,
    }

    headers = {'Content-Type': 'application/json'}
    response = requests.post(endpoint, json=data, headers=headers)
    result = response.json()
    if result.get('payUrl'):
        return redirect(result['payUrl'])
    else:
        messages.error(request, "Không thể kết nối ví MoMo, vui lòng thử lại sau.")
        return redirect('checkout')

@login_required
def checkout_view(request):
    cart = Cart(request)
    if request.method == "POST":
        form = CheckoutForm(request.POST)
        if form.is_valid():
            address = form.cleaned_data['address']
            phone = form.cleaned_data['phone']
            payment_method = form.cleaned_data['payment_method']

            # 1. Tạo đối tượng Order, thêm trường payment_method
            order = Order.objects.create(
                user=request.user,
                address=address,
                phone=phone,
                payment_method=payment_method,
                total_price=cart.get_total_price()
            )

            # 2. Tạo các OrderItem
            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    price=item['price'],
                    quantity=item['quantity']
                )

            # 3. Xoá giỏ hàng
            cart.clear()

            # 4. Xử lý theo phương thức thanh toán
            if payment_method == 'momo':
                return redirect('momo_payment', order_id=order.id)  # giả sử bạn có url name là 'momo_payment'
            elif payment_method == 'bank':
                messages.info(request, "Vui lòng chuyển khoản theo thông tin trên đơn hàng.")
                return redirect('order_detail', order_id=order.id)
            else:  # COD
                messages.success(request, "Đặt hàng thành công! Vui lòng chuẩn bị tiền khi nhận hàng.")
                return redirect('order_detail', order_id=order.id)
    else:
        form = CheckoutForm()

    return render(request, 'app/checkout.html', {'form': form, 'cart': cart})

def product_list_view(request):
    sort = request.GET.get('sort', '')  # lấy param sort từ URL, ví dụ ?sort=price_asc hoặc ?sort=newest

    if sort == 'price_asc':
        products = Product.objects.all().order_by('price')
    elif sort == 'newest':
        products = Product.objects.all().order_by('-created_at')
    else:
        products = Product.objects.all()

    return render(request, 'app/product_list.html', {
        'products': products,
        'current_sort': sort,
    })


def search(request):
    return render(request, 'app/search_results.html')


def home_view(request):
    products = Product.objects.all()
    featured_products = Product.objects.filter(is_featured=True)[:3]  # nếu có trường is_featured
    return render(request, 'app/home.html', {
        'products': products,
        'featured_products': featured_products
    })


# def home(request):
#     all_products = list(Product.objects.all())
#     featured_products = random.sample(all_products, min(3, len(all_products)))
#     return render(request, 'app/home.html', {'featured_products': featured_products})

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
            redirect_url = request.GET.get('next') or 'home'
            return redirect(redirect_url)

    else:
        form = UserCreationForm()
    return render(request, "app/register.html", {"form": form})

def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            redirect_url = request.GET.get('next') or 'home'
            return redirect(redirect_url)

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
    reviews = product.reviews.order_by('-created_at')
    message = None

    if request.method == "POST" and "review_submit" in request.POST:
        name = request.POST.get("name", "").strip()
        rating = request.POST.get("rating")
        content = request.POST.get("content", "").strip()
        if name and rating and content:
            Review.objects.create(
                product=product,
                name=name,
                rating=int(rating),
                content=content
            )
            return redirect('product_detail', slug=product.slug)
        else:
            message = "Bạn phải nhập đầy đủ thông tin đánh giá!"

    return render(request, 'app/detail.html', {
        'product': product,
        'flavors': flavors,
        'weights': weights,
        'reviews': reviews,
        'message': message,
    })


def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))
    cart.add(product, quantity)
    product_url = reverse('product_detail', args=[product.slug])
    return redirect(f"{product_url}?added=true")

def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect('cart_detail')

def cart_detail(request):
    cart = Cart(request)
    return render(request, 'app/cart_detail.html', {'cart': cart})

@staff_member_required
def admin_orders_view(request):
    orders = Order.objects.all().order_by('-created_at')
    return render(request, 'app/admin_orders.html', {'orders': orders})

def search_view(request):
    query = request.GET.get('q', '')
    results = Product.objects.filter(name__icontains=query)
    return render(request, 'app/search_results.html', {'results': results, 'query': query})

def blog_view(request):
    posts = [
        {
            'title': 'Lợi ích của việc uống đủ nước mỗi ngày',
            'content': 'Uống đủ nước giúp duy trì sự cân bằng chất lỏng trong cơ thể, tăng cường năng lượng và cải thiện làn da...',
        },
        {
            'title': 'Tập thể dục đều đặn để tăng cường sức khỏe',
            'content': 'Tập thể dục giúp cải thiện hệ tim mạch, giảm stress và nâng cao sức đề kháng của cơ thể...',
        },
        {
            'title': 'Chế độ ăn giàu vitamin và khoáng chất',
            'content': 'Bổ sung rau xanh, hoa quả và các loại hạt giúp cung cấp vitamin và khoáng chất cần thiết cho cơ thể...',
        },
    ]

    return render(request, 'app/blog.html', {'posts': posts})
