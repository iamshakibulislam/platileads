import imp
import requests
from bs4 import BeautifulSoup
import tldextract
import openai
from django.shortcuts import render
from dashboard.custom_scripts import *

def search_on_google(domain,position,scraperapikey):
    #extract domain and tld and add them together using tdlextract
    domain_tld = tldextract.extract(domain)
    domain_tld = domain_tld.domain + '.' + domain_tld.suffix

    get_content = requests.get(f"http://api.scraperapi.com?api_key={scraperapikey}&url=https://google.com/search?q={position}+at+{domain}&gl=us&hl=en")

    soup = BeautifulSoup(get_content.content,'lxml')


    all_h3_tags = soup.find_all('h3')
    list_of_title = []
    for h3 in all_h3_tags:
        try:
            if h3 != None and h3 != "":
                list_of_title.append(h3.string)

        except:
            pass

    return list_of_title


    

def extract_name_and_position(list_of_search_titles,position):
    astring = ""

    for title in list_of_search_titles:
        if title != None and title != "":
            astring += title + " "

    response_name = openai.Completion.create(
	  model="text-davinci-002",
	  prompt=f"extract only a name of a {position} and nothing else from the following text : {astring}",
	  temperature=0.7,
	  max_tokens=35,
	  top_p=1,
	  frequency_penalty=0,
	  presence_penalty=0
	)

    response_position = openai.Completion.create(
	  model="text-davinci-002",
	  prompt=f"extract one job position name from the following text : {astring}",
	  temperature=0.7,
	  max_tokens=35,
	  top_p=1,
	  frequency_penalty=0,
	  presence_penalty=0
	)

    return [str(response_name.choices[0].text).strip(),str(response_position.choices[0].text).strip()]





def return_email_found_status(request,first_name,last_name,domain,credit_deduct_amount):
    #extract only domain name from url

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
                sel_user_credit = user_credit.objects.get(user=request.user)
                sel_user_credit.credits_remaining -= int(credit_deduct_amount)
                sel_user_credit.save()
                
                return str(possible_email.replace(' ',''))
            
            else:
                return None
