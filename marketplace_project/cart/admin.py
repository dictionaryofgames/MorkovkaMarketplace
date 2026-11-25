from django.contrib import admin
from .models import Cart, CartItem


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'session_key_preview', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('user__username', 'session_key')
    inlines = [CartItemInline]

    def session_key_preview(self, obj):
        return obj.session_key[:20] + '...' if len(obj.session_key) > 20 else obj.session_key
    session_key_preview.short_description = 'Session Key'
