from validate_email import validate_email
from bs4 import BeautifulSoup
from email_scraper import scrape_emails
from func_timeout import func_timeout, FunctionTimedOut,func_set_timeout
import tldextract
import requests
import threading



print('STARTING DMAIL SCRAPER......... ')
print('\n')

print('DMAIL IS ACTIVE NOW.........')
print('\n')

print('DMAIL SCRAPER IS READY TO RECIEVE INPUT.........\n')

print('NOTE : FOR MASS EMAIL FINDING CREATE A FILE WITH NAME domains.txt AND PUT EACH DOMAIN LINE BY LINE" \n')

#userinput=input('PLEASE INPUT URL or domains.txt  FILE PATH : ')

guestpost_only= "no"
'''
if guestpost_only.lower() == 'yes' or guestpost_only.lower() == 'true':
	print("Finding only guestpost oportunities...... \n")

else:
	print('finding emails for every domain even without guestpost oportunities............\n')

'''
single_domain = True
'''
check_action_type = userinput.split('.')

if 'txt' in check_action_type or 'text' in check_action_type:
	single_domain = False
'''

#starting action for single domain 

already_scraped_domains = []





def crawl_and_find_emails(domain_name,row_num=1,request=None,total_rows=100):
	#function for crawling and finding emails only
	check_root_doamin = tldextract.extract(domain_name)
	root_domain = check_root_doamin.domain+'.'+check_root_doamin.suffix
	print('finding email on ',root_domain)
	headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36"}
	req=requests.get('https://'+root_domain,headers=headers,timeout=110)
	soup=BeautifulSoup(req.content,'lxml')
	
	
	all_the_unverified_links = []
	all_the_verified_links = []
	for a in soup.find_all('a'):
		if a.get('href') == None or '@' in a.get('href'):
			
			pass
		else:
			all_the_unverified_links.append(a.get('href'))


	all_the_unverified_links = list(set(all_the_unverified_links))

	


#filtering links (only allowing links that are from same domain for better analysis)

	for lnk in all_the_unverified_links:
		get_root_domain = tldextract.extract(lnk)
		check_this_link_domain = get_root_domain.domain+'.'+get_root_domain.suffix
		
		if check_this_link_domain == root_domain and len(lnk.split(get_root_domain.suffix)[1]) <= 40:
			all_the_verified_links.append(lnk)

		elif lnk != None and lnk != '' and len(lnk) != 0 and lnk[0] == '/' and len(lnk) <= 40:
			all_the_verified_links.append('https://'+root_domain+lnk)



	#variable conditioning to set email found or any guestpost oporunity found or not 
	found_email = None

	found_guest_post_op = False
	

	#guestpost keywords

	patterns = [

		"guest-post",
		"guest-posts",
		"guest_posts",
		"guest-posting",
		"guest-blog",
		"guest-contribution",
		"contribute",
		"write-for-us",
		"write_for_us",
		"write-for",
		"writting-for",
		"write-to",
		"write_to_us",
		"write-to-us",
		"write_for",
		"submit-post",
		"submit-your-post",
		"contribute",
		"guest-article",
		"guest_article",
		"guest-author",
		"guest-blogging",
		"guest-post-guideline",
		"contribution-guideline",
		"contributing-writer",
		"guest-column",
		"guest_column",
		"suggest-a-ppost",
		"suggest-posts",
		"post-suggesions",
		"post-suggesion",
		"submit-post",
		"submit-an-article",
		"submit-article",
		"submit-your",
		"share-your",
		"submit_an_article",
		"contributor",
		"guest-poster-wanted",
		"guest-blogger",
		"accepting-guest",
		"accepting_guest",
		"writer_wanted",
		"writers-wanted",
		"writer-wanted",
		"become-a-writer",
		"become-an-author",
		"become-a-guest-writer"


		]

	contact_patterns = [


		"contact",
		"support",
		"help",
		"customer",
		"get",
		"touch",
		"email",
		"about",
		"info",
		"reach"


	]



	
	

	new_links = [item for item in all_the_verified_links if any(substring in item for substring in contact_patterns)]




	#checking if these patterns found in all the verified links
	
	for pattern in patterns:
		if pattern in str(all_the_verified_links):
			
			found_guest_post_op = True
			print('guest post oportunity found..')
			break

	
	#finding emails from all the verified links and break when found one
	if (found_guest_post_op == True or guestpost_only.lower() == 'no' or guestpost_only.lower() == 'false') and len(all_the_verified_links) < 200:

		for links in new_links:
			try:


				#continue checking untill found_email is not None
				if found_email == None:
					print('checking on ', links)
					headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36"}
					req=requests.get(links,headers=headers,timeout=10)
					#opening verified links and scraping web html content
					linksoup=BeautifulSoup(req.content,'lxml')

					sc_email = scrape_emails(str(linksoup))

					if len(list(sc_email)) != 0 and list(sc_email)[0] != 'email@example.com':
						searched_email = list(sc_email)[0]
						
						

						#checking the found email is valid or not(junk email or not)
						if ((str(searched_email.split('@')[1]).lower() == str(root_domain) or str(searched_email.split('@')[1]).lower() == 'gmail.com' or str(searched_email.split('@')[1]).lower() == 'yahoo.com' or str(searched_email.split('@')[1]).lower() == 'hotmail.com' or str(searched_email.split('@')[1]).lower() == 'aol.com' ) and str(searched_email.split('@')[0]).lower() != 'sales'):
							
							found_email = searched_email
							break

						else:
							#incase email is not relevant to the domain
							
							print('email found but invalid ! ' ,searched_email, ' retrying.......... \n')


						



					else:
						pass

				#here is the logic for found guestpost oportunity but not email logic
				




				else:
					break
			except :
				pass


		#found guest post oporunity but no email found logic and store guestpost links ina file name guest_post_links.txt
		if found_guest_post_op == True and found_email == None:

			for pattern in patterns:

				get_guest_post_url = [url for url in all_the_verified_links if pattern in url]

				if len(get_guest_post_url) != 0:
					print('could not find email but saving guest post url:',get_guest_post_url[0])
					#open_file = open('guest_post_links.txt','a')

					#open_file.write(get_guest_post_url[0]+'\n')

					#open_file.close()

					break

							

					


	

	#just displaying messages if email and guest post oporunity found or not
	if found_email != None:
		print('Email found and saved...', found_email)
		

	elif found_email == None and found_guest_post_op == True:
		print('Could not find email but found guest post oporunity - saving.... ')
		

	else:
		print('email can not be found')
		





	sel_user_inst = request.user
	curr_proc = sel_user_inst.file_process_percentage
	sel_user_inst.file_process_percentage = float((1/total_rows)*100)+float(curr_proc)
	sel_user_inst.save()


	return {"found_email":found_email,"row_num":row_num}


