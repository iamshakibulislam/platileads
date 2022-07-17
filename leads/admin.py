from django.contrib import admin
from .models import *
from django.utils.html import format_html



admin.site.register(campaign_leads)

@admin.register(campaigns)
class campaignsAdmin(admin.ModelAdmin):
    
    list_display = ('name','date','user__email')
    search_fields = ('name','date','user__email')
    ordering = ('date',)


    
    def user__email(self,obj):
        return obj.user.email
    def user__phone(self,obj):
        return obj.user.phone





@admin.register(leads)
class leadsAdmin(admin.ModelAdmin):
    list_display = ('date','first_name','last_name','position','email','website','position','linkedin_profile')
    search_fields = ('date','first_name','last_name','email','website','linkedin_profile','phone','position')
    ordering = ('date',)

    list_filter = ('position',)

    list_per_page = 100


    

    