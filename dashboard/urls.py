from django.urls import path
from . import views

urlpatterns = [
    path('',views.dashboard_home,name='dashboard_home'),
    path('email_verification/',views.email_verification,name='email_verification'),
    path('bulk_email_verification/',views.bulk_email_verification,name='bulk_email_verification'),
    path('bulk_email_verification_result/',views.bulk_email_verification_result,name='bulk_email_verification_result'),
    path('download_bulk_email_verification_file/',views.download_bulk_email_verification_file,name='download_bulk_email_verification_file'),
    path('find_email/',views.find_email,name='find_email'),
    path('find_bulk_email/',views.find_bulk_email,name='find_bulk_email'),
    path('find_bulk_email_result/',views.find_bulk_email_result,name='find_bulk_email_result'),
    path('download_bulk_email_found_file/',views.download_bulk_email_found_file,name='download_bulk_email_found_file'),
    path('find_author_email/',views.find_author_email,name='find_author_email'),
    path('bulk_author_leads/',views.bulk_author_leads,name='bulk_author_leads'),
    path('bulk_author_leads_results/',views.bulk_author_leads_results,name='bulk_author_leads_results'),
    path('contact_us/',views.contact_us,name="contact_us"),
    path('backlink_builder/',views.backlink_builder,name='backlink_builder'),
    path('backlink_result/',views.backlink_result,name='backlink_result'),
    path('bulk_guest_post_file/',views.download_bulk_guestpost_file,name="download_guestpost_file"),
    path('email_verification_ext/',views.email_verification_ext,name="email_verification_ext"),
    
]
