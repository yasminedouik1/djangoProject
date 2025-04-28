from django.contrib import admin
from .models import MenuItem, Basket, Order, OrderItem, UserProfile

class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'created_at')
    list_filter = ('category',)
    search_fields = ('name',)

class BasketAdmin(admin.ModelAdmin):
    list_display = ('user', 'menu_item', 'quantity', 'created_at')
    list_filter = ('user',)
    search_fields = ('user__username', 'menu_item__name')

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'user_phone_number', 'user_address', 'status', 'created_at')
    list_filter = ('status', 'user')
    search_fields = ('user__username',)

    def user_phone_number(self, obj):
        return obj.user.profile.phone_number if obj.user.profile.phone_number else 'N/A'
    user_phone_number.short_description = 'Phone Number'

    def user_address(self, obj):
        return obj.user.profile.address if obj.user.profile.address else 'N/A'
    user_address.short_description = 'Address'

class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'menu_item', 'quantity')
    list_filter = ('order',)
    search_fields = ('menu_item__name',)

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'address')
    search_fields = ('user__username', 'phone_number', 'address')

admin.site.register(MenuItem, MenuItemAdmin)
admin.site.register(Basket, BasketAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)
admin.site.register(UserProfile, UserProfileAdmin)