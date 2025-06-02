from django.contrib import admin
from .models import Product, Order, OrderItem

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price']

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'address', 'phone', 'get_total', 'created_at']
    list_filter = ['created_at', 'user']
    search_fields = ['user__username', 'address']
    inlines = [OrderItemInline]

    def get_total(self, obj):
        return obj.get_total()

    get_total.short_description = 'Tổng tiền'
