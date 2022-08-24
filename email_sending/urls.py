from django.urls import path
from . import views

urlpatterns = [
    path('add_campaign_email/', views.add_campaign_email, name='add_campaign_email'),
    path('sender_list/', views.sender_list, name='sender_list'),
    path('upload_contacts/', views.upload_contacts, name='upload_contacts'),
    path('process_contacts/',views.process_contacts,name="process_contacts")
    
]
