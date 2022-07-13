from django.urls import path
from . import views

urlpatterns = [
    path('single_lead/',views.single_lead,name='single_lead'),
]
