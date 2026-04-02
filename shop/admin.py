from django.contrib import admin
from shop.models import Contact,Cart,Product
from .models import Order, CartItem

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 1  # Allows adding one extra item directly in the order admin

class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'created_at']  # Display order info in the list view
    inlines = [CartItemInline]  # Allows you to add/edit CartItems directly within an Order

class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'name', 'price', 'quantity']  # Display user and other fields in admin list view

admin.site.register(Cart, CartAdmin)

# Register your models here.
admin.site.register(Order, OrderAdmin)
admin.site.register(Contact)
admin.site.register(Product)