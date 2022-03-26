from django.urls import path
from . import views

urlpatterns = [
    path('subscribe/',views.subscribe,name='subscribe'),
    path('create_payment_intent/',views.create_payment_intent,name='create_payment_intent'),
    path('thank-you/',views.thank_you,name='thank_you'),
    path('webhook/',views.webhook,name='webhook'),
    path('user-subscriptions/',views.subscriptions,name='subscriptions'),
    path('cancel_subscription/',views.cancel_subscription,name='cancel_subscription'),
]
