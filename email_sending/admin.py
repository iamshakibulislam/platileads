from django.contrib import admin
from .models import *

@admin.register(emails_for_campaign)
class emails_for_campaignAdmin(admin.ModelAdmin):
    list_display = ['user','email','created_at','updated_at']
   
    search_fields = ['email','user__email']
    list_per_page = 20


@admin.register(uploaded_files)
class uploaded_filesAdmin(admin.ModelAdmin):
    list_display = ['user_email']
    search_fields = ['user__email']
    list_per_page = 20

    def user_email(self,obj):
        return obj.user.email


@admin.register(sending_campaigns)
class sending_campaignsAdmin(admin.ModelAdmin):
    list_display = ['campaign_name','email','created_at','updated_at','is_active']
    search_fields = ['campaign_name','email__email','email__user__email']
    list_per_page = 20


@admin.register(email_messages)
class email_messagesAdmin(admin.ModelAdmin):
    list_display = ['campaign','subject','message','delivery_date','created_at','updated_at']
    search_fields = ['campaign__campaign_name','campaign__email__email','campaign__email__user__email','subject']
    list_per_page = 20


@admin.register(contact_campaign)
class contact_campaignAdmin(admin.ModelAdmin):
    list_display = ['name','created_at','updated_at']
    search_fields = ['name','user__email']
    list_per_page = 20


@admin.register(contact_list)
class contact_listAdmin(admin.ModelAdmin):
    list_display = ['contact_campaign','email','created_at','updated_at']
    search_fields = ['contact_campaign__name','email','contact_campaign__user__email']
    list_per_page = 20

@admin.register(sending_campaign_track)
class sending_campaign_trackAdmin(admin.ModelAdmin):
    list_display = ['campaign','opened_total','replied_total','followedup_total','total_sent','created_at','updated_at']
    search_fields = ['campaign__campaign_name','campaign__email__email','campaign__email__user__email','email']
    list_per_page = 20


admin.site.register(sending_track)
    

    
