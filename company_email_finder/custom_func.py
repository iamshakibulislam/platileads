import imp
import requests
from bs4 import BeautifulSoup
import tldextract
import openai
from django.shortcuts import render
from dashboard.custom_scripts import *
import json
import csv


def read_csv_file(filepath):
	op = open(filepath,'r')
	csv_read = csv.DictReader(op,delimiter=',')

	
	data = []
	


	for x in csv_read:
		data.append(x)

	headers = list(data[0].keys())

	op.close()

	return {"data":data,"headers":headers}

#write to csv file- headers must be a list of strings and data must be a list of dictionaries
def write_csv_file(filepath,headers,data):
	op = open(filepath,'w')
	fieldnames = headers
	csv_write = csv.DictWriter(op,fieldnames=fieldnames,delimiter=',')

	csv_write.writeheader()

	for dt in data:
		csv_write.writerow(dt)

	op.close()


	return filepath

def search_on_google(domain,position,scraperapikey):
    #extract domain and tld and add them together using tdlextract
    domain_tld = tldextract.extract(domain)
    domain_tld = domain_tld.domain + '.' + domain_tld.suffix

    get_content = requests.get(f"https://api.proxycrawl.com/scraper?token={scraperapikey}&url=https://google.com/search?q={position}+at+{domain}&gl=us&hl=us")



    jsony=json.loads(get_content.content)
    

    title_list = []

    for title in jsony["body"]['searchResults']:
        title_list.append(title["title"])

    

    return title_list


    

def extract_name_and_position(list_of_search_titles,position):
    astring = ""

    for title in list_of_search_titles:
        if title != None and title != "":
            astring += title + " "

    response_name = openai.Completion.create(
	  model="text-davinci-002",
	  prompt=f"extract all the names from the following text who are {position} and separate names by comma : {astring}",
	  temperature=0.7,
	  max_tokens=35,
	  top_p=1,
	  frequency_penalty=0,
	  presence_penalty=0
	)


    return str(response_name.choices[0].text).strip()





def return_email_found_status(first_name,last_name,domain):
    #extract only domain name from url
        try:
            root_domain_inst = tldextract.extract(domain)
            root_domain = root_domain_inst.domain+'.'+root_domain_inst.suffix

            possible_combinations = []
            possible_combinations.append(first_name+'@'+root_domain)
            possible_combinations.append(first_name+'.'+last_name+'@'+root_domain)
            
            possible_combinations.append(last_name+'@'+root_domain)
            possible_combinations.append(last_name+'.'+first_name+'@'+root_domain)
            possible_combinations.append(last_name+'-'+first_name+'@'+root_domain)
            possible_combinations.append(last_name+'_'+first_name+'@'+root_domain)
            possible_combinations.append(first_name+'-'+last_name+'@'+root_domain)
            possible_combinations.append(first_name+'_'+last_name+'@'+root_domain)
            possible_combinations.append(first_name[0]+last_name+'@'+root_domain)
            possible_combinations.append(first_name+last_name+'@'+root_domain)

            get_mx = get_mx_records_domain(root_domain)[-1]

            #print('your mx record is:',get_mx)
            for possible_email in possible_combinations:
                check_valid_or_not = is_valid_email(get_mx,possible_email)

            

                if check_valid_or_not == True:
                    '''
                    sel_user_credit = user_credit.objects.get(user=request.user)
                    sel_user_credit.credits_remaining -= int(credit_deduct_amount)
                    sel_user_credit.save()
                    '''
                    
                    return possible_email.replace(' ','')
                
                else:
                    '''
                    sel_user_credit = user_credit.objects.get(user=request.user)
                    sel_user_credit.credits_remaining -= 1
                    sel_user_credit.save()
                    '''

                    return None
        except:
            return None
