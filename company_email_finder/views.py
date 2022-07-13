import imp
from turtle import pos
from django.shortcuts import render
from numpy import full
from dashboard.custom_scripts import *
from .custom_func import *
from django.http import HttpResponse
from django.conf import settings as st
import openai

openai.api_key = st.OPENAI_API_KEY

def single_lead(request):
    if request.method == "GET":
        return render(request, 'company_leads/single_lead.html')


    if request.method == "POST":
        get_domain = request.POST.get('domain')
        get_position = request.POST.get('position')
        scraperapikey = st.SCRAPER_API_KEY

        get_list_of_title_from_google = search_on_google(get_domain,get_position,scraperapikey)

        #add all title from the list into a single string every item is separated by full stop
        astring = ""
        for title in get_list_of_title_from_google:
            if title != None and title != "":
                astring += title + "."

        
        #get the name and position from the string
        name_and_position = list(extract_name_and_position(astring,get_position))

       
        try:
            full_name = name_and_position[0]
        except:
            full_name = None

        try:
            position = name_and_position[1]
            position = position.replace("Linkedin","")
            position = position.replace("Facebook","")
            position = position.replace("linkedin","")
        except:
            position = None

        if full_name != None and len(full_name.split(" ")) == 3:
            first_name = full_name.split(" ")[0]
            last_name = full_name.split(" ")[1]

        elif full_name != None and len(full_name.split(" ")) == 2:
            first_name = full_name.split(" ")[0]
            last_name = full_name.split(" ")[1]

        elif full_name != None and len(full_name.split(" ")) == 1:
            first_name = full_name.split(" ")[0]
            last_name = ""

        else:
            first_name = None
            last_name = None

        #find email address from firstname and lastname and domain
        
        if first_name != None and last_name != None:
            
            found_email = return_email_found_status(request,first_name,last_name,get_domain,4)
            if found_email != None:
                return HttpResponse(found_email)
            else:
                return HttpResponse("No email found")
           
           
            
        else:
            return HttpResponse("No email found")
    


