from django.urls import path
from . import views

urlpatterns = [
    path('single_lead/',views.single_lead,name='single_lead'),
    path('bulk_leads/',views.bulk_leads,name='bulk_leads'),
    path('bulk_leads_results/',views.bulk_leads_results,name='bulk_leads_results'),
]
