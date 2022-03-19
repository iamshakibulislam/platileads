from django.urls import path
from . import views

urlpatterns = [
    path('subscribe/',views.subscribe,name='subscribe'),
    path('create_payment_intent/',views.create_payment_intent,name='create_payment_intent'),
]
