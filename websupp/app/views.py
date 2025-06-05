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
POSTS = [
    {
        'id': 1,
        'title': 'Lợi ích của việc uống đủ nước mỗi ngày',
        'content': '''
Uống đủ nước không chỉ giúp cơ thể duy trì cân bằng chất lỏng mà còn cải thiện chức năng não bộ, hỗ trợ tiêu hóa và giúp làn da khỏe mạnh.

Nước đóng vai trò quan trọng trong việc vận chuyển chất dinh dưỡng, điều hòa nhiệt độ cơ thể và loại bỏ độc tố. Nếu bạn thường xuyên cảm thấy mệt mỏi, đau đầu hoặc khô da, có thể cơ thể bạn đang thiếu nước.

Hãy bắt đầu ngày mới với một ly nước ấm và duy trì thói quen uống khoảng 2 lít nước mỗi ngày để cải thiện sức khỏe toàn diện.
''',
        'image': 'https://sasukegym.vn/wp-content/uploads/2021/03/vai-tro-nuoc-voi-nguoi-tap-the-hinh.jpg',
    },
    {
        'id': 2,
        'title': 'Tập thể dục đều đặn để tăng cường sức khỏe',
        'content': '''
Tập thể dục giúp giảm nguy cơ mắc các bệnh mãn tính như tiểu đường, tim mạch, béo phì, đồng thời cải thiện tinh thần và giấc ngủ.

Bạn không cần phải đến phòng gym mỗi ngày. Đi bộ nhanh, đạp xe, nhảy dây, yoga hay thậm chí là lau nhà cũng đều mang lại lợi ích. Điều quan trọng là duy trì thói quen vận động ít nhất 30 phút mỗi ngày.

Hãy lựa chọn môn thể thao bạn yêu thích để việc rèn luyện trở nên thú vị và bền vững hơn.
''',
        'image': 'https://images.unsplash.com/photo-1558611848-73f7eb4001a1',
    },
    {
        'id': 3,
        'title': 'Chế độ ăn giàu vitamin và khoáng chất',
        'content': '''
Một chế độ ăn đa dạng với rau củ, trái cây, ngũ cốc nguyên hạt và các loại hạt sẽ giúp cung cấp đầy đủ vitamin và khoáng chất cần thiết cho cơ thể.

Vitamin C từ cam, chanh giúp tăng sức đề kháng. Sắt trong rau bina hỗ trợ sản sinh hồng cầu. Omega-3 trong cá giúp não bộ hoạt động tốt hơn.

Hãy ưu tiên thực phẩm tự nhiên, hạn chế đồ chế biến sẵn và duy trì bữa ăn đều đặn mỗi ngày.
''',
        'image': 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c',
    },
    {
        'id': 4,
        'title': 'Ngủ đủ giấc – Bí quyết vàng cho sức khỏe toàn diện',
        'content': '''
Giấc ngủ giúp cơ thể hồi phục, cân bằng hormone và tái tạo tế bào. Người lớn nên ngủ từ 7–9 tiếng mỗi đêm để đảm bảo sức khỏe thể chất và tinh thần.

Thiếu ngủ có thể dẫn đến béo phì, giảm trí nhớ, lo âu và nhiều bệnh mãn tính khác. Hãy tạo một môi trường ngủ yên tĩnh, tránh ánh sáng xanh từ điện thoại trước giờ ngủ.

Một giấc ngủ chất lượng là nền tảng cho một cơ thể khỏe mạnh.
''',
        'image': 'https://cdn.nhathuoclongchau.com.vn/unsafe/800x0/https://cms-prod.s3-sgn09.fptcloud.com/ngu_du_giac_bi_quyet_tang_cuong_suc_khoe_the_va_tinh_than_3_6bf4ce11c9.png',
    },
    {
        'id': 5,
        'title': 'Thư giãn và giảm stress bằng thiền và hít thở sâu',
        'content': '''
Căng thẳng kéo dài ảnh hưởng đến hệ miễn dịch, huyết áp và tâm trạng. Thiền và hít thở sâu là hai phương pháp đơn giản giúp bạn thư giãn tinh thần và phục hồi năng lượng.

Dành 10 phút mỗi ngày để tập trung vào hơi thở, loại bỏ suy nghĩ tiêu cực và sống trọn vẹn với hiện tại. Bạn có thể kết hợp nghe nhạc nhẹ, ngồi ở nơi yên tĩnh hoặc ra ngoài thiên nhiên.

Thói quen thư giãn thường xuyên giúp bạn sống cân bằng và hạnh phúc hơn.
''',
        'image': 'https://vttu.edu.vn/wp-content/uploads/2024/10/Thien-2.jpeg',
    },
    {
        'id': 6,
        'title': 'Tăng cường miễn dịch bằng thói quen lành mạnh',
        'content': '''
Một hệ miễn dịch khỏe mạnh giúp cơ thể chống lại vi khuẩn, virus và bệnh tật. Để làm được điều này, bạn cần kết hợp nhiều yếu tố: chế độ ăn uống đầy đủ, ngủ ngon, tập thể dục và tránh stress.

Ngoài ra, bổ sung thực phẩm chứa kẽm, vitamin D, probiotics và uống nước ấm đều đặn cũng rất hữu ích.

Đừng quên rửa tay thường xuyên và giữ vệ sinh cá nhân để hạn chế lây nhiễm bệnh từ môi trường.
''',
        'image': 'https://suckhoedoisong.qltns.mediacdn.vn/324455921873985536/2021/9/30/1-1632967777959596819251.png',
    },
]

def blog_view(request):
    return render(request, 'app/blog.html', {'posts': POSTS})

def blog_detail_view(request, post_id):
    post = next((p for p in POSTS if p['id'] == post_id), None)
    if not post:
        return render(request, '404.html', status=404)
    return render(request, 'app/blog_detail.html', {'post': post})
