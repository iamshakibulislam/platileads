from django.urls import path
from . import views


urlpatterns = [
    path('test_email_connection/',views.test_email_connection,name='test_email_connection'),
    path('add_email/',views.add_email,name='add_email'),
    path('warmup_stats/',views.warmup_stats,name='warmup_stats'),
    path('testimage/',views.testimage,name='testimage'),
    
]