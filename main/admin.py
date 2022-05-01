from django.contrib import admin

from .models import Product, ProductState, ProductTracking


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('code', 'user',)


@admin.register(ProductState)
class ProductCardStateAdmin(admin.ModelAdmin):
    list_display = (
        'code', 'product_name', 'current_price', 'old_price',)


@admin.register(ProductTracking)
class CardTrackingAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'product', 'end_tracking', 'interval')
