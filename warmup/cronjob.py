from .models import *

from users.models import *
import smtplib
import email.mime.multipart
from email.mime.text import MIMEText
from imap_tools import *
import re
from .custom_func import *
from datetime import datetime,timedelta
import random
from django.conf import settings as st
import openai
openai.api_key = st.OPENAI_API_KEY




def warmup_emails():

    all_active_campaigns = warmup_campaign.objects.filter(is_active=True)

    for camp in all_active_campaigns:
        if camp.end_at < datetime.now().date():
            camp.is_active = False
            camp.save()
            continue
        sel_user_credit = user_credit.objects.get(user=camp.user)
        if sel_user_credit.credits_remaining < 2:
            continue

        sel_stats = warmup_track.objects.get(campaign=camp)
        sel_stats.today_sent = 0
        sel_stats.save()

        today_sending_limit = 0

        
            #check message quota and send messages if quota is not maxed

        sel_stat_for_curr_camp = warmup_track.objects.get(campaign=camp)

        campaign_duration = (camp.end_at-camp.created_at.date()).days

            #get all the total_sent  possible values

        all_total_sent_outcome = series_total(camp.start_count,camp.increament_count,campaign_duration)
        #setting up daily sending limit here
        for total_limit in all_total_sent_outcome:
            if total_limit > sel_stat_for_curr_camp.total_sent:
                today_sending_limit = int(total_limit - sel_stat_for_curr_camp.total_sent)
                break


        #now set todays sending limit for this campaign and after every operation it will be deducted from the total.
        all_active_emails = [em.email for em in all_active_campaigns]
        try:
            list_all_unseen_msg = list_unseen_mails(camp.email,camp.app_password,all_active_emails)
        except:
            continue

        all_email_replied = []

        for msg in list_all_unseen_msg:
            from_message = msg['message_from']
            folder_ = msg['folder']

            if folder_ == 'spam':
                #select campaign of the message from and update the from email stats
                from_camp = warmup_campaign.objects.filter(email=from_message)
                max_id = max([x.id for x in from_camp])
                final_from_camp = warmup_campaign.objects.get(id=max_id)

                sel_from_camp_stat = warmup_track.objects.get(campaign=final_from_camp)

                sel_from_camp_stat.spam_count += 1
                sel_from_camp_stat.moved_to_inbox +=1

                sel_from_camp_stat.save()

            
            #do actions with the main campaign in the loop and send replies to the senders

            if today_sending_limit > 0:

                all_email_replied.append(msg['message_from'])

                generate_message = create_message()

                send_the_reply = send_reply(msg['email'],camp.app_password,msg['message_id'],msg['subject'],generate_message,msg['message_from'],camp.user.first_name)

                if send_the_reply == True:
                    sel_user_credit = user_credit.objects.get(user=camp.user)
                    if sel_user_credit.credits_remaining < 2:
                        continue
                    sel_user_credit.credits_remaining -= 2
                    sel_user_credit.save()

                    today_sending_limit -= 1
                    sel_stat_for_curr_camp.today_sent += 1
                    sel_stat_for_curr_camp.save()
                    sel_stat_for_curr_camp.total_sent += 1
                    sel_stat_for_curr_camp.save()

            
            else:
                break

        #list all the possible recipients of the campaign and send them the message

        all_potential_recipients = []

        for cam in all_active_campaigns:
            if cam.email not in all_email_replied and cam.email != camp.email:

                all_potential_recipients.append(cam.email)

        
        #shuffle the all potential recipiens
        random.shuffle(all_potential_recipients)

        #send the message to the recipients

        if len(all_potential_recipients) != 0 and today_sending_limit > 0:
            counter = 0
            for r in range(today_sending_limit):
                sub_line=create_subject()
                crt_msg = create_message()
                try:
                    recipient = all_potential_recipients[counter]
                except IndexError:
                    random.shuffle(all_potential_recipients)
                    counter = 0
                    recipient = all_potential_recipients[counter]

                counter +=1

                send_the_msg=send_email_message(camp.email,camp.app_password,sub_line,crt_msg,recipient,camp.user.first_name)
                
                if send_the_msg == True:
                    sel_user_credit = user_credit.objects.get(user=camp.user)
                    if sel_user_credit.credits_remaining < 2:
                        continue
                    sel_user_credit.credits_remaining -= 2
                    sel_user_credit.save()

                    sel_stat_for_curr_camp.today_sent += 1
                    sel_stat_for_curr_camp.save()
                    sel_stat_for_curr_camp.total_sent += 1
                    sel_stat_for_curr_camp.save()

                else:
                    pass

        




    


        







        
        

        




