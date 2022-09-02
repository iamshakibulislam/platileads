from http.client import HTTPResponse
from .custom import *
from datetime import datetime,timedelta
from django.http import HttpResponse
from threading import Thread



def send_email_campaign():

    #first filter all the message which is to delivered today
    today_is_to_send = email_messages.objects.filter(delivery_date = datetime.now().date()).filter(campaign__is_active=True)
    #print(today_is_to_send.values())

    for msg in today_is_to_send:

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
                tracking_str = f"""
                
                
            <table id=":1d7" cellpadding="0" role="presentation" class="cf gz ac0"><tbody>
            <tr><td><div class="cKWzSc mD" idlink="" tabindex="0" role="button" jslog="21576; u014N:cOuCgd,Kr2w4b;">
            <img class="mL" id="platileads" camp="{sel_camp.id}" cont_id="{reci.id}" src="https://a828-202-173-123-195.ngrok.io/email_sending/blank_image/?camp={sel_camp.id}&cont_id={reci.id}" alt=""></div></td><td>
            </td><td><div class="XymfBd mD" idlink="" tabindex="0" role="button" jslog="21578; u014N:cOuCgd,Kr2w4b;">
             </div></td><td></td>
            <td class="io"><div class="adA"></div></td></tr></tbody></table>
                
                """

            #message is ready to send

            final_message = main_message+tracking_str

            
            #now send the message and make sure to create new thread for each message 
            pass

            #setup smtp server here

            try:
                smtp_server_inst = smtplib.SMTP_SSL('smtp.gmail.com',465)   
                smtp_server_inst.login(sel_camp.email.email,sel_camp.email.app_password)

                th = Thread(target=email_send,args=(msg.subject,final_message,sel_camp.email.email,reci.email,sel_camp.email.user.first_name,smtp_server_inst,sel_camp.email.user.id,sel_camp.id))
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
        

    