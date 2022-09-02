from django.urls import path
from . import views

urlpatterns = [
    path('add_campaign_email/', views.add_campaign_email, name='add_campaign_email'),
    path('sender_list/', views.sender_list, name='sender_list'),
    path('upload_contacts/', views.upload_contacts, name='upload_contacts'),
    path('process_contacts/',views.process_contacts,name="process_contacts"),
    path('contacts_book/',views.contacts_book,name='contacts_book'),
    path('delete_contact_book/',views.delete_contact_book,name='delete_contact_book'),
    path('get_contacts/', views.get_contacts, name='get_contacts'),
    path('delete_contact/',views.delete_contact,name='delete_contact'),
    path('email_campaign/',views.email_campaign,name='email_campaign'),
    path('render_followup/',views.render_followup,name='render_followup'),
    path('save_campaign/',views.save_campaign,name='save_campaign'),
    path('blank_image/',views.blank_image,name='blank_image'),
    path('campaigns/',views.campaigns,name='campaigns'),
    path('change_campaign_status/',views.change_campaign_status,name='change_campaign_status'),
    path('test_email_send/',views.test_email_send,name='test_email_send')
    
]
