from django.contrib import admin
from .models import *



@admin.register(packages)
class packagesAdmin(admin.ModelAdmin):
    list_display = ('name','credits','price_per_month','price_per_year')
    search_fields = ('name','credits','price_per_month','price_per_year')


@admin.register(subscription_data)
class subscription_dataAdmin(admin.ModelAdmin):
    list_display = ('user__first_name','user__last_name','user__email','package','start_date','expire_date','is_active','last_update')
    search_fields = ('user__first_name','user__last_name','user__email','user__phone','package','start_date','expire_date','is_active','last_update')
    list_filter = ('package__name',)
    ordering = ('start_date',)

    def user__first_name(self,obj):
        return obj.user.first_name

    def user__last_name(self,obj):
        return obj.user.last_name

    def user__email(self,obj):
        return obj.user.email
    def user_phone(self,obj):
        return obj.user.phone

    def package(self,obj):
        return obj.package
