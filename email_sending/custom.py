from users.models import *
from .models import *
from dashboard.models import *
import re
import json
import smtplib
from email.message import EmailMessage
import pandas as pd

import smtplib
import email.mime.multipart
from email.mime.text import MIMEText
from bs4 import BeautifulSoup
from imap_tools import *
import random
from time import sleep



#function to fill a text placeholder from query set
#make sure while input queryset give query set as dictionary by using
#queryset.objects.values()
#for filtered queryset --->  filteredqueryset.values()-->iterate -->run function inside

def fill_message(message,queryset):
	message = message
	pattern = re.compile(r"\{[\s\w]+[\|]?[\w\s]*\}")
	all_tags = pattern.findall(message)

	for tag in all_tags:
		
		sp = tag.split("|")

		if len(sp) == 2:
			main_tag = sp[0][1:].replace(" ","")
			fallback = sp[1][:-1].replace(" ","")

		elif(len(sp)==1):
			main_tag = sp[0][1:-1].replace(" ","")
			fallback = ""

		else:
			pass

		#override the message and return the msg

		

		try:
			message=message.replace(tag,queryset[main_tag])
		except:
			message=message.replace(tag,fallback)


		
	return message




#email sending function
#smpt server setup first before calling function. Then just pass the server instance to the function
#smtp_server_inst = smtplib.SMTP_SSL(smtp_server,465)   
#smtp_server_inst.login(from_,app_password)

def email_send(subject,body,from_,to,fname,smtp_server_inst,uid,campid):
	html_message = body

	msg = EmailMessage()
	msg['Subject'] = subject
	msg['From'] = f"{fname}<{from_}>"
	msg['To'] = to
	#msg["Bcc"] = "shakibulislammuk@gmail.com"
	#msg.add_header('Reply-To',f"shakibulislammuk@gmail.com,{from_}")
	

	msg.add_alternative(

	html_message,subtype='html'

		)


	

	try:
		
		rn = random.randint(3,15)
		sleep(int(rn))
		smtp_server_inst.send_message(msg)
		print('successfully sent to ',to)
		sel_user=user_credit.objects.get(user=User.objects.get(id=int(uid)))
		sel_user.credits_remaining -= 2

		sel_user.save()
		try:
			sel_camp_track=sending_campaign_track.objects.get(campaign=sending_campaigns.objects.get(id=int(campid)))
			sel_camp_track.total_sent += 1
			sel_camp_track.save()
		
		except sending_campaign_track.DoesNotExist :
			sending_campaign_track.objects.create(campaign=sending_campaigns.objects.get(id=int(campid)),total_sent=1)
		return True

	except:
		print('email sending failed')
		return False
			
	



def reply_track(camp_id):
	sel_camp = sending_campaigns.objects.get(id=int(camp_id))
	sender_email = sel_camp.email.email
	app_password = sel_camp.email.app_password
	get_subject = email_messages.objects.filter(campaign=sel_camp)[0].subject

	#browse emails using imap tools

	mailbox = MailBox('imap.gmail.com').login(sender_email, app_password)

	ff=mailbox.fetch(criteria=f'TEXT "{get_subject}"',mark_seen=False)

	for x in ff:

		try:

			print('--------------\n')

			#print('subject is : ',x.subject,'uid is : ',x.uid,' from is - ',x.from_,' reply to is : ',x.reply_to,' message is ',x.html)
			
			soup = BeautifulSoup(x.html,'lxml')

			st=soup.find('img',id=re.compile(r'platileads'))
			

			pattern = re.compile(r"camp=\d+\&[\w\;\s]+\=\d+")

			find = pattern.findall(str(st))

			print("find is ",find)

			splitText = find[0].split('&')

			

			camp = None
			cont_id = None

			for x in splitText:
				if "camp" in x:
					camp=x.split("=")[-1]
				
					
				
				if "cont_id" in x:
					
					cont_id=x.split("=")[-1]
					
					
				

			sel_replied_camp = sending_campaigns.objects.get(id=int(camp))
			sel_replied_cont = contact_list.objects.get(id=int(cont_id))



			sel_sending_track = sending_track.objects.get(campaign=sel_replied_camp,sent_to=sel_replied_cont)
			if sel_sending_track.is_replied == False:
				sel_sending_track.is_replied = True
				sel_sending_track.save()

				sel_sending_campaign_track = sending_campaign_track.objects.get(campaign=sel_replied_camp)
				sel_sending_campaign_track.replied_total += 1
				sel_sending_campaign_track.save()

		except:
			pass




