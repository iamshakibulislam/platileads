from django.contrib import admin
from .models import User, appsumo_deals,coupon_codes,user_credit

@admin.register(appsumo_deals)
class appsumo_dealsAdmin(admin.ModelAdmin):
    list_display = ('code','is_active','updated_at')
    search_fields = ('code','updated_at')

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