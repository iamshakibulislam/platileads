from django.urls import path
from . import views

urlpatterns = [
    path('add_bank_account/',views.add_bank_account,name='add_bank_account'),
    path('request_payout/',views.request_payout,name='request_payout'),
]
