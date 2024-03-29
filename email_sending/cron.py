from http.client import HTTPResponse
from .custom import *
from datetime import datetime,timedelta
from django.http import HttpResponse
from threading import Thread
from django.utils import timezone

from time import sleep



def send_email_campaign():

    #first filter all the message which is to delivered today

    print("hi shakil")

    print(email_messages.objects.filter(delivery_date__lte=timezone.now()))

    today_is_to_send = email_messages.objects.filter(delivery_date__lte = timezone.now()).filter(campaign__is_active=True).filter(is_sent=False)
    print('tday ',today_is_to_send)
    #print(today_is_to_send.values())

    for msg in today_is_to_send:
        # mark as sent
        emai_msg = email_messages.objects.get(id=msg.id)
        emai_msg.is_sent = True
        emai_msg.save()

        # check all the campaign recipients 
        sel_camp = msg.campaign
        sel_contact_book = sel_camp.contact_book
        all_recipients = contact_list.objects.filter(contact_campaign = sel_contact_book)
        
        for reci in all_recipients:
            replied = False

            try:
                sel_track=sending_track.objects.get(campaign=sel_camp,sent_to=reci)
                replied = sel_track.is_replied
            except sending_track.DoesNotExist:
                sending_track.objects.create(campaign=sel_camp,sent_to=reci)

            
            if replied == False:

                #now send the email to this recepient
                dict_obj_for_reci = contact_list.objects.filter(id=reci.id)
                main_message = fill_message(msg.message,dict_obj_for_reci.values()[0])
                main_subject = fill_message(msg.subject,dict_obj_for_reci.values()[0])
                tracking_str = f"""
                
                
            <table id=":1d7" cellpadding="0" role="presentation" class="cf gz ac0"><tbody>
            <tr><td><div class="cKWzSc mD" idlink="" tabindex="0" role="button" jslog="21576; u014N:cOuCgd,Kr2w4b;">
            <img class="mL" id="platileads" camp="{sel_camp.id}" cont_id="{reci.id}" src="https://bigisoft.com/email_sending/blank_image/?camp={sel_camp.id}&cont_id={reci.id}" alt=""></div></td><td>
            </td><td><div class="XymfBd mD" idlink="" tabindex="0" role="button" jslog="21578; u014N:cOuCgd,Kr2w4b;">
             </div></td><td></td>
            <td class="io"><div class="adA"></div></td></tr></tbody></table>
                
                """

            #message is ready to send
                
            try:

                final_message = main_message+tracking_str
                main_subject = main_subject
            except:
                continue

            
            #now send the message and make sure to create new thread for each message 
            

            #setup smtp server here

            try:
                smtp_server = sel_camp.email.provider
                smtp_port = sel_camp.email.smtp_port
                smtp_server_inst = smtplib.SMTP_SSL(smtp_server,int(smtp_port))   
                smtp_server_inst.login(sel_camp.email.email,sel_camp.email.app_password)

                sleep(5)

                th = Thread(target=email_send,args=(main_subject,final_message,sel_camp.email.email,reci.email,sel_camp.email.user.first_name,smtp_server_inst,sel_camp.email.user.id,sel_camp.id))
                th.start()

                #email_send(msg.subject,final_message,sel_camp.email.email,reci.email,sel_camp.email.user.first_name,smtp_server_inst,sel_camp.email.user.id)
            
            except:
                pass





    return HttpResponse("ok")




#check for reply functionality

def check_reply():

    #sel email messages which dellivery date was in the last 7 days

    sel_email_messages = email_messages.objects.filter(delivery_date__gte= (datetime.now() - timedelta(days=7)).date())

    

    camp_list = []

    for msg in sel_email_messages:
        if msg.campaign.id in camp_list:
            pass
        else:
            camp_list.append(msg.campaign.id)

    for camp_id in camp_list:
        th= Thread(target=reply_track,args=(camp_id,))
        th.start()
        

    