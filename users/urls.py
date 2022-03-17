from django.urls import path
from . import views


urlpatterns = [
    path('signup/',views.signup,name='signup'),
    path('login/',views.login,name='login'),
    path('change_alert_status/',views.change_alert_status,name='change_alert_status'),
]
