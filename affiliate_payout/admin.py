from django.contrib import admin
from .models import *


#register payout requests model in djagno admin
@admin.register(payout_requests)
class payout_requestsAdmin(admin.ModelAdmin):
    list_display = ['user','amount','payment_method__bank_name','payment_method__account_number','payment_method__branch_name','payment_method__routing_number','is_paid','created_at']
    list_filter = ['is_paid']
    search_fields = ['user__first_name','user__last_name','user__email']
    ordering = ['-created_at']
    
    
    list_per_page = 10

    def payment_method__bank_name(self,obj):
        return obj.payment_method.bank_name

    def payment_method__account_number(self,obj):
        return obj.payment_method.account_number

    def payment_method__branch_name(self,obj):
        return obj.payment_method.branch_name
    
    def payment_method__routing_number(self,obj):
        return obj.payment_method.routing_number



#register payout requests model in djagno admin
@admin.register(bank_account_details)
class bank_account_detailsAdmin(admin.ModelAdmin):
    list_display = ['user','bank_name','account_number','branch_name','routing_number','account_type','created_at']
   
    search_fields = ['user__first_name','user__last_name','user__email']
    ordering = ['-created_at']
    
    
    list_per_page = 10
    
    
    

   