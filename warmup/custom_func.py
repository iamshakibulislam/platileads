from .models import *
from users.models import *
import smtplib
import email.mime.multipart
from email.mime.text import MIMEText
from imap_tools import *
import re
from datetime import datetime,timedelta
import openai
from django.conf import settings as st
from func_timeout import *


openai.api_key = st.OPENAI_API_KEY


@func_set_timeout(30)
def test_email_connection_status(email,app_password,smtp_server,smtp_port):
	print("testing email connectivity")
	try:
		context = smtplib.SMTP_SSL(smtp_server, int(smtp_port))
		context.login(email,app_password)
		return True
	
	except:
		return False
	


@func_set_timeout(900)
def list_unseen_mails(email,app_password,warm_list):

	pattern = re.compile(r"'message-id': \(+\'\<[a-zA-Z\w+\.+\=+\-+\@+]+")


	email_data = []

	mailbox = MailBox('imap.gmail.com').login(email, app_password)
	mailbox.folder.set('INBOX')

	fetch_mailbox = mailbox.fetch(AND(seen=False))

	for msg in fetch_mailbox:
		find_msg = pattern.findall(str(msg.headers))
		msgidpattern = re.compile(r"[a-zA-Z\w+\d+\.+\-+\=+]+\@+[\w+\.+\-+]+")

		message_id = msgidpattern.findall(str(find_msg))

		message_from = str(msg.from_)
		
		if message_from.strip() in warm_list:
			email_data.append({"message_from":message_from,"message_id":message_id[0],"email":email,"app_password":app_password,"folder":"inbox","subject":msg.subject,"uid":msg.uid,"moved_to_inbox":False})

	mailbox.folder.set('[Gmail]/Spam')
	fetch_mailbox = mailbox.fetch(AND(seen=False))

	for msg in fetch_mailbox:
		find_msg = pattern.findall(str(msg.headers))
		msgidpattern = re.compile(r"[a-zA-Z\w+\d+\.+\-+\=+]+\@+[\w+\.+\-+]+")

		message_id = msgidpattern.findall(str(find_msg))

		message_from = str(msg.from_)

		mailbox.move(msg.uid,'INBOX')

		if message_from.strip() in warm_list:

			email_data.append({"message_from":message_from,"message_id":message_id[0],"email":email,"app_password":app_password,"folder":"spam","subject":msg.subject,"uid":msg.uid,"moved_to_inbox":True})




	return email_data




def send_reply(email,app_password,message_id,subject,message,to,first_name):
	try:

		msg = MIMEText(message)
		msg['to'] = to
		msg['from'] = f"{first_name}<{email}>"
		msg['subject'] = f"Re:{subject}"
		msg.add_header('In-Reply-To', message_id)
		server = smtplib.SMTP_SSL('smtp.gmail.com')
		server.login(email,app_password)
		server.sendmail(msg['from'], [msg['to']], msg.as_string())

		print("successfully sent reply to - ",to)
		return True
	
	except:
		return False



def send_email_message(email,app_password,subject,message,to,first_name):
	try:

		msg = MIMEText(message)
		msg['to'] = to
		msg['from'] = f"{first_name}<{email}>"
		msg['subject'] = f"{subject}"
		
		server = smtplib.SMTP_SSL('smtp.gmail.com')
		server.login(email,app_password)
		server.sendmail(msg['from'], [msg['to']], msg.as_string())

		print("successfully sent message to - ",to," from ",msg['from'])
		return True
	
	except:
		return False
	




#this function is for showing total sent emails outcomes values during entire campaign duration.
#so that later we can  use this to calculate daily sending limit. formula [todays_total_outcome-total_sent_so_far] = today_limit
def series_total(start,step,period):
	total_l = []
	past = start
	for x in range(period):
		
		if len(total_l) == 0:
			total_l.append(start)
		
		elif len(total_l) == 1:
			past = total_l[0]+step
			total_l.append(total_l[0]+step+total_l[0])
			
		else:
			total_l.append(total_l[-1]+step+past)
			past =  step+past
		
		print(past,'total pattern is - ',total_l)
			
	
	return total_l




def create_subject():
	astring = ""


	response_name = openai.Completion.create(
	  model="text-davinci-002",
	  prompt=f"create an email short subject line under 6 words",
	  temperature=0.7,
	  max_tokens=35,
	  top_p=1,
	  frequency_penalty=0,
	  presence_penalty=0
	)

	return str(response_name.choices[0].text).strip()



def create_message():
	astring = ""


	response_name = openai.Completion.create(
	  model="text-davinci-002",
	  prompt=f"create an email short message under 20 words",
	  temperature=0.7,
	  max_tokens=35,
	  top_p=1,
	  frequency_penalty=0,
	  presence_penalty=0
	)

	return str(response_name.choices[0].text).strip()