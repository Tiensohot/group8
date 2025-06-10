from app.models import Product

# Lấy 3 sản phẩm đầu tiên và đặt is_featured = True
products = Product.objects.all()[:3]
for p in products:
    p.is_featured = True
    p.save()

print("Đã cập nhật 3 sản phẩm thành nổi bật!")