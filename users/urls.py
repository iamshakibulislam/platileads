from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('signup/',views.signup,name='signup'),
    path('login/',views.login,name='login'),
    path('change_alert_status/',views.change_alert_status,name='change_alert_status'),
    path('profile/',views.profile,name='profile'),
    path('logout/',views.logout,name='logout'),
    path('process_percentage/',views.process_percentage,name='process_percentage'),
    path('appsumo_code/',views.appsumo_code,name='appsumo_code'),
    #password reset urls
    path('password-reset/',auth_views.PasswordResetView.as_view(template_name='users/reset.html',html_email_template_name='users/password-reset-email-template.html'),name='password_reset'),
    path('password-reset-done/',auth_views.PasswordResetDoneView.as_view(template_name='users/reset-email.html'),name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/',auth_views.PasswordResetConfirmView.as_view(template_name='users/reset-conf.html'),name='password_reset_confirm'),
    path('password-reset-complete/',auth_views.PasswordResetCompleteView.as_view(template_name='users/reset-suc.html'),name='password_reset_complete'),
]
