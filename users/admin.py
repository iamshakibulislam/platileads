from django.contrib import admin
from .models import User,coupon_codes,user_credit,user_coupon

@admin.register(user_coupon)
class user_couponAdmin(admin.ModelAdmin):
    list_display = ('email','code','has_redeemed','date')
    search_fields = ('email','code','has_redeemed','date')

@admin.register(user_credit)
class user_creditAdmin(admin.ModelAdmin):
    list_display = ('user__first_name','user__last_name','user__email','credits_remaining')
    
    search_fields = ('user__first_name','user__last_name','user__email','user__phone','credits_remaining')

    def user__first_name(self,obj):
        return obj.user.first_name
    def user__last_name(self,obj):
        return obj.user.last_name
    def user__email(self,obj):
        return obj.user.email
    def user__phone(self,obj):
        return obj.user.phone
    


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('join_date','first_name','last_name','email','phone')
   # list_filter = ('first_name','last_name','email','phone')
    search_fields = ('first_name','last_name','phone','email','join_date')
    ordering = ('join_date',)

@admin.register(coupon_codes)
class coupon_codesAdmin(admin.ModelAdmin):
    list_display = ('code','discount','bonus_credit')
    
    search_fields = ('code','discount')
    ordering = ('created_at',)