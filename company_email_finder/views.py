
import imp
from django.shortcuts import redirect, render
from numpy import full
from dashboard.custom_scripts import *
from .custom_func import *
from django.http import HttpResponse
from django.conf import settings as st
import openai
from dns import resolver
import smtplib
import csv
from openpyxl import load_workbook,Workbook
import os
from functools import wraps
from django.http import HttpResponse
from users.models import *
from .models import *
from leads.models import *
from subscriptions.models import *
import json
from func_timeout import *

openai.api_key = st.OPENAI_API_KEY

def single_lead(request):
    if request.method == "GET":
        
        curr_sub = subscription_data.objects.get(user=request.user)
        curr_sub_plan = curr_sub.package.name

        plan = None

        if curr_sub_plan == "FREE" or curr_sub_plan == "free":
            plan = "FREE"

        
        
        return render(request, 'company_leads/single_lead.html',{'plan':plan})


    if request.method == "POST":
        get_domain = request.POST.get('domain')
        get_position = request.POST.get('position')
        scraperapikey = st.SCRAPER_API_KEY

        try:
            get_domain =get_domain.split('//')[1]
        except:
            pass

        #get credits remaining
        cred = user_credit.objects.get(user=request.user)
        if cred.credits_remaining <5:
            return HttpResponse("You don't have enough credits")


        try:
            get_list_of_title_from_google = search_on_google(get_domain,get_position,scraperapikey)

        except TypeError:
            get_list_of_title_from_google = search_on_google(get_domain,get_position,scraperapikey)

        except:
            return HttpResponse("Something Went Wrong ! Please Try Again")

       

        #add all title from the list into a single string every item is separated by full stop
        astring = ""
        for title in get_list_of_title_from_google:
            if title != None and title != "":
                astring += title + "."

        
        #get the name and position from the string
        names = extract_name_and_position(astring,get_position).split(",")

        

        for name in names:

            try:
                full_name = name.encode('ascii','ignore').decode('ascii').strip()
            except:
                full_name = None

        

            if full_name != None and len(full_name.split(" ")) == 3:
                first_name = full_name.split(" ")[0]
                last_name = full_name.split(" ")[2]

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
                try:
                    found_email = return_email_found_status(first_name,last_name,get_domain)
                except:
                    found_email = None
                
                if found_email != None:

                    


                    
                    try:
                        if return_email_found_status(first_name+'1',last_name+'1',get_domain) != None:
                            found_email = None
                            break
                    except:
                        found_email = None
                        break

                    sel_user_credit = user_credit.objects.get(user=request.user)
                    sel_user_credit.credits_remaining -= 5
                    sel_user_credit.save()

                    save_lead = leads()
                    save_lead.user = request.user
                    save_lead.first_name = first_name
                    save_lead.last_name = last_name
                    save_lead.email = found_email.lower()
                    save_lead.website = get_domain
                    save_lead.position = get_position
                    save_lead.save()

                    get_active_campaign = campaigns.objects.get(user=request.user,is_active=True)

                    campaign_leads_inst = campaign_leads()
                    campaign_leads_inst.campaign = get_active_campaign
                    campaign_leads_inst.lead = save_lead
                    campaign_leads_inst.save()

                    
                    return render(request,'company_leads/components/found_email.html',{'email':found_email,'position':get_position,'first_name':first_name,'last_name':last_name})
                else:
                    pass
            
            
        try:
            if found_email == None:    
        
                sel_user_credit = user_credit.objects.get(user=request.user)
                sel_user_credit.credits_remaining -= 1
                sel_user_credit.save()
                return render(request,'company_leads/components/found_email.html',{'not_found':True})

        except:
            return render(request,'company_leads/components/found_email.html',{'not_found':True})
            



def bulk_leads(request):
    if request.method == "GET":
        
        curr_sub = subscription_data.objects.get(user=request.user)
        curr_sub_plan = curr_sub.package.name
        
        plan = None

        if curr_sub_plan == "FREE" or curr_sub_plan == "free":
            plan = "FREE"
        

        return render(request, 'company_leads/bulk_leads.html',{'plan':plan})

    if request.method == "POST":

        get_all_the_uploaded_files = lead_file.objects.filter(uploaded_by=request.user)

        if len(get_all_the_uploaded_files) == 0:
            pass
        else:
            try:
                for file in get_all_the_uploaded_files:
                    os.remove(file.uploaded_file.path)
                    file.delete()
            
            except:
                pass
        

        
        try:
            csv_file=request.FILES['file']
            save_the_file = lead_file()
            save_the_file.uploaded_by = request.user
            save_the_file.uploaded_file = csv_file
            save_the_file.save()

            #get the file name
            file_name = save_the_file.uploaded_file.name
            file_path = save_the_file.uploaded_file.path
            get_file_data=read_csv_file(file_path)
            headers = get_file_data["headers"]

            return render(request,'company_leads/components/column_selector.html',{'all_columns':headers})

            





        except:
            return HttpResponse("Something Went Wrong ! Please Try Again")


def bulk_leads_results(request):
    if request.method == "GET":
        return HttpResponse("Request method not allowed")

    if request.method == "POST":
        get_all_the_uploaded_files = lead_file.objects.filter(uploaded_by=request.user)

        the_last_file = get_all_the_uploaded_files.last()
        total_found = 0
        domain = request.POST.get('website_column')
        job_position = request.POST.get('job_position')

        headers = None
        data = None

        if domain != None and job_position != None:
            read_file=read_csv_file(the_last_file.uploaded_file.path)
            headers = read_file["headers"]

            headers.append('first_name')
            headers.append('last_name')
            headers.append('email')

            data = read_file["data"]

            new_data = []
            
            try:
                sel_user_inst = request.user
                sel_user_inst.file_process_percentage = float(0)
                sel_user_inst.save()

            except:
                pass

            i = 1
            for dt in data:

                sel_user_inst = request.user
                sel_user_inst.file_process_percentage = float((i/len(data))*100)
                sel_user_inst.save()

                i+=1

                #check if  the user has enough credits or not
                select_user_credit = user_credit.objects.get(user=request.user)
                if select_user_credit.credits_remaining < 5:
                    break

                

                get_list_of_title_from_google = None
                #search on google the name of the position (CEO/CO-FOUNDER/etc)
                try:
                    get_list_of_title_from_google = search_on_google(dt[domain],job_position,st.SCRAPER_API_KEY)
                
                except TypeError:
                    get_list_of_title_from_google = search_on_google(dt[domain],job_position,st.SCRAPER_API_KEY)

                except:
                    get_list_of_title_from_google = None

                if get_list_of_title_from_google != None:
                    astring = ""

                    for title in get_list_of_title_from_google:
                        if title != None and title != "":
                            astring += title + "."

                    #extract all the names from the search result string

                    names = extract_name_and_position(astring,job_position).split(",")

                    #print(astring,' and ','whole names ',names)

                    for name in names:
                        print("the name is ",name)

                        try:
                            full_name = name.encode('ascii', 'ignore').decode('ascii').strip()
                        except:
                            full_name = None

                    

                        if full_name != None and len(full_name.split(" ")) == 3:
                            first_name = full_name.split(" ")[0]
                            last_name = full_name.split(" ")[2]

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

                        #print(first_name,'-->',last_name)
                        try:
                            dt[domain] = dt[domain].split('//')[1]
                        except:
                            pass
                        
                        if first_name != None and last_name != None:
                            try:
                                found_email = return_email_found_status(first_name,last_name,dt[domain])
                            
                            except:
                                found_email = None

                            
                            
                            
                            if found_email != None:

                                
                                try:
                                    if return_email_found_status(first_name+'1',last_name+'1',dt[domain]) != None:
                                        found_email = None
                                        break
                                except:
                                    found_email = None
                                    break

                                sel_user_credit = user_credit.objects.get(user=request.user)
                                sel_user_credit.credits_remaining -= 5
                                sel_user_credit.save()

                                save_lead = leads()
                                save_lead.user = request.user
                                save_lead.first_name = first_name
                                save_lead.last_name = last_name
                                save_lead.email = found_email.lower()
                                save_lead.website = dt[domain]
                                save_lead.position = job_position
                                save_lead.save()

                                get_active_campaign = campaigns.objects.get(user=request.user,is_active=True)

                                campaign_leads_inst = campaign_leads()
                                campaign_leads_inst.campaign = get_active_campaign
                                campaign_leads_inst.lead = save_lead
                                campaign_leads_inst.save()

                                new_dt = dt.copy()
                                new_dt["first_name"] = first_name
                                new_dt["last_name"] = last_name
                                new_dt["email"] = found_email

                                new_data.append(new_dt)

                                total_found += 1

                                break


                            else:
                                pass


                try:
                    if found_email == None:
                        sel_user_credit = user_credit.objects.get(user=request.user)
                        sel_user_credit.credits_remaining -= 5
                        sel_user_credit.save()

                        new_dt = dt.copy()
                        new_dt["first_name"] = first_name
                        new_dt["last_name"] = last_name
                        new_dt["email"] = "not found"

                        new_data.append(new_dt) 

                except:
                    pass      

            
            #write the data to a csv file
            write_into_file=write_csv_file(the_last_file.uploaded_file.path,headers,new_data)

            return render(request,'company_leads/components/show_download_button.html',{'total_found':total_found,'download_url': the_last_file.uploaded_file.url})


                    


        




        
   