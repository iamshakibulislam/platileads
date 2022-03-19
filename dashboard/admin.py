from django.contrib import admin
from  django.contrib.auth.models  import  Group

admin.site.unregister(Group)
admin.site.site_header = "Platileads Admin Portal"
admin.site.site_title = "Platileads"
admin.site.index_title = "Welcome To Administration Portal"

from dashboard.models import file_uploader

admin.site.register(file_uploader)
