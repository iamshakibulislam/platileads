from django.urls import path
from . import views

urlpatterns = [
    path('',views.dashboard_home,name='dashboard_home'),
    path('email_verification/',views.email_verification,name='email_verification'),
    path('bulk_email_verification/',views.bulk_email_verification,name='bulk_email_verification'),
    
]
