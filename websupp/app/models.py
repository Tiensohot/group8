from bson.json_util import default
from djongo import models
from django.contrib.auth.models import User
from django.utils import timezone

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)  # để tạo đường dẫn chi tiết đẹp
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    image = models.ImageField(upload_to='products/')
    flavor_options = models.CharField(max_length=300, blank=True)  # ví dụ: "Vanilla, Chocolate"
    weight_options = models.CharField(max_length=200, blank=True)  # ví dụ: "5lbs, 10lbs"
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    def __str__(self):
        return self.name

class Order(models.Model):
    PAYMENT_METHODS = [
        ('cod', 'Thanh toán khi nhận hàng'),
        ('momo', 'Ví Momo'),
        ('bank', 'Chuyển khoản ngân hàng'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=200)
    address = models.TextField()
    phone = models.CharField(max_length=20)
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(default="Đang xử lý", max_length=50)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHODS, default='cod')  # thêm trường này

    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"

    def get_total(self):
        return sum(item.get_total_price() for item in self.items.all())

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.product} x {self.quantity}"

    def get_total_price(self):
        return self.product.price * self.quantity if self.product else 0


class Review(models.Model):
    product = models.ForeignKey('Product', related_name='reviews', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    rating = models.PositiveSmallIntegerField(default=5)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)