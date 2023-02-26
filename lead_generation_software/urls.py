
from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.home_page,name='home_page'),
    path('users/',include('users.urls')),
    path('dashboard/',include('dashboard.urls')),
    path('leads/',include('leads.urls')),
    path('subscriptions/',include('subscriptions.urls')),
    path('about-us/',views.about_us,name='about_us'),
    path('terms-and-conditions/',views.terms_and_conditions,name='terms_and_conditions'),
    path('privacy-policy/',views.privacy_policy,name='privacy_policy'),
    path('company_email_finder/',include('company_email_finder.urls')),
    path('affiliates/',views.affiliates,name='affiliates'),
    path('affiliate_payout/',include('affiliate_payout.urls')),
    path('warmup/',include('warmup.urls')),
    path('email_sending/',include('email_sending.urls')),
    path('backlink_builder/',views.backlink_builder,name='backlink_builder')
]


urlpatterns+=static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)