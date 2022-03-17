from django.urls import path
from . import views

urlpatterns = [
    path('create_campaign/',views.create_campaign,name='create_campaign'),
    path('campaign_list/',views.campaign_list,name='campaign_list'),
    path('delete_campaign/',views.delete_campaign,name='delete_campaign'),
    path('show_leads/<int:pk>/',views.show_leads,name='show_leads'),
    path('delete_lead/',views.delete_lead,name='delete_lead'),
    path('export_lead/<int:pk>/',views.export_lead,name='export_lead'),
    path('activate_campaign/',views.activate_campaign,name='activate_campaign'),
    path('capture_leads/',views.capture_leads,name='capture_leads'),
]
