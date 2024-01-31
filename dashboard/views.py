#from http.client import HTTPResponse

import email
from logging import root
from django.shortcuts import render,redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from time import sleep
from bs4 import BeautifulSoup
import requests
from func_timeout import *
from users.models import *
from leads.models import *
from xls2xlsx import XLS2XLSX
import tldextract
from functools import wraps
from subscriptions.models import *
import os
import csv
from django.views.decorators.csrf import csrf_exempt
from .custom_scripts import *
from .models import *
from func_timeout import *
from save_thread_result import ThreadWithResult
import re
import threading
from company_email_finder.custom_func import *
from django.conf import settings as st
from company_email_finder.models import *
from .guestpostscript import *
openai.api_key = st.OPENAI_API_KEY





@login_required(login_url='/users/login/')
def download_bulk_guestpost_file(request):
    get_file_instance = file_uploader.objects.filter(user=request.user)
    get_file_path = get_file_instance[0].file.url
    actual_file_path = ""
    file_extension = get_file_path.split('.')[-1]

    if file_extension == "xls":
        actual_file_path = get_file_path[:-3]+"xlsx"
    
    elif file_extension == "csv":
        actual_file_path = get_file_path[:-3]+"xlsx"
    
    elif file_extension == "xlsx":
        actual_file_path = get_file_path

    else:
        return HttpResponse("Invalid File")
    
    
    return redirect(actual_file_path)






def backlink_result(request):

    if request.method == 'POST':
        get_column_name = request.POST.get('column_name')
        get_file_instance = file_uploader.objects.filter(user=request.user)
        get_file_path = get_file_instance[0].file.path
        actual_file_path = ""
        file_extension = get_file_path.split('.')[-1]

        if file_extension == "xls":
            actual_file_path = get_file_path[:-3]+"xlsx"
           
        elif file_extension == "csv":
            actual_file_path = get_file_path[:-3]+"xlsx"

        elif file_extension == "xlsx":
            actual_file_path = get_file_path
        
        else:
            return HttpResponse("Invalid File")

        information = xlsx_info(actual_file_path)

        all_columns = information['column_names']
        total_columns = information['total_columns']
        total_rows = information['total_rows']

        get_the_email_column_position = all_columns.index(get_column_name)+1
        total_email_verified = 0
        try:
            sel_user_inst = request.user
            sel_user_inst.file_process_percentage = float(0)
            sel_user_inst.save()

        except:
            pass

        all_threads = []

        for row_num in range(1,total_rows+1):
            
            try:
                

                sel_user_credit_inst = user_credit.objects.get(user=request.user)
                if sel_user_credit_inst.credits_remaining == 0:
                    break
                email_val = xlsx_retrive_column_data(row_num,get_the_email_column_position,actual_file_path)
                

                if email_val != None and email_val != "":
                
                    #do email validation here and write the result in the same column
                    if row_num == 1:
                        
                        xlsx_write_on_new_column(row_num,total_columns,"Contact Email",actual_file_path)

                    else:


                        thread = ThreadWithResult(target=crawl_and_find_emails,args=(email_val,row_num,request,total_rows))
                        
                        
                        thread.start()

                        all_threads.append(thread)

            except:
                pass


        #join all the thread ie - wait for all of them to finish workings

        for thread in all_threads:
            thread.join()



        thread_results = []

        #place all the threads output in the thread_result list . the format of the output is 
        #{"found_email":"youremail@gmail.com","row_num":1}

        for th in all_threads:

            try:
            
                print("the result is - ",th.result)
                thread_results.append(th.result)

            except:
                pass


        #thread result putting into csv

        for result in thread_results:
            try:
                xlsx_write_on_new_column(result["row_num"],total_columns,result["found_email"],actual_file_path)
                
                sel_user_credit = user_credit.objects.get(user=request.user)
                sel_user_credit.credits_remaining -= 1
                sel_user_credit.save()

                if result["found_email"] != None and result["found_email"] != "" and result["found_email"] != " " and len(result["found_email"]) != 0:
                    total_email_verified +=1

            except:
                pass
                            


        
        return render(request,'dashboard/components/show_download_button_for_guestpost.html',{'total_verified':total_email_verified})



@login_required(login_url='/users/login/')
def backlink_builder(request):
    if request.method == "GET":
        return render(request,"dashboard/bulk_guestpost_oportunity_finder.html")

    if request.method == "POST":
        try:
            get_this_user_files = file_uploader.objects.filter(user=request.user)
            for file in get_this_user_files:
                try:
                    os.remove(file.file.path)
                except:
                    pass
                try:
                    os.remove(file.file.path[:-3]+"xlsx")
                except:
                    pass
                file.delete()
        except:
            pass
        get_file = request.FILES.get('file')

        file_instance = file_uploader(user=request.user,file=get_file)


        file_instance.save()

        file_path = file_instance.file.path
        
        #check file extension
        file_extension = file_path.split('.')[-1]


        if file_extension == "xls":
            new_file_path = file_path[:-3]+"xlsx"
            thexls = XLS2XLSX(file_path)
            thexls.to_xlsx(new_file_path)

            information = xlsx_info(new_file_path)


        
        

        elif file_extension == "csv":

            #convert csv to xlsx

            print("here is the file path : ",file_path, "and file name :",file_instance.file.name)
            

            check= csv_to_xlsx(file_path,file_instance.file.name)
            new_path = file_instance.file.path[:len(file_instance.file.path)-3]+"xlsx"
            information = xlsx_info(new_path)
           
           # file_instance.file.path=file_instance.file.path[:len(file_instance.file.path)-3]+"xlsx"
            

        elif file_extension == "xlsx":

        
            information = xlsx_info(file_path)

        else:
            print("removing file path and extensions")
            os.remove(file_instance.file.path)
            return HttpResponse("invalid_file_extension")

        all_columns = information['column_names']



        return render(request,'dashboard/components/backlink_column_selection.html',{'all_columns':all_columns})










def get_affiliate_data(request):
    if request.user.is_affiliate == True:
        balance = round(request.user.balance,2)

        all_referred = User.objects.filter(referred_by=request.user)
        total_referred = len(all_referred)

        all_referred_user = subscription_data.objects.filter(user__referred_by=request.user)
        all_prem_user=all_referred_user.exclude(package__name='FREE')


        return {"total_referred":total_referred,"balance":balance,"all_prem_user":len(all_prem_user),"all_referred_user":all_referred_user,'all_referred_user_count':len(all_referred_user)}


    else:
        return None




@login_required(login_url='/users/login/')
def dashboard_home(request):
    sel_campaigns = campaigns.objects.filter(user=request.user)
    total_campaigns = len(sel_campaigns)
    total_leads = 0

    for campaign in sel_campaigns:
        total_leads_for_this_camp= campaign_leads.objects.filter(campaign=campaign).count()
        total_leads += total_leads_for_this_camp

    get_user_credit_inst = user_credit.objects.get(user=request.user)
    credits_remaining = get_user_credit_inst.credits_remaining

    all_latest_leads = campaign_leads.objects.filter(campaign__user=request.user)[:100]

    get_token = str(request.user.secret_id)
    aff_data = None
    if request.user.is_affiliate:
        aff_data = get_affiliate_data(request)
        

    return render(request,'dashboard/index.html',{'total_campaigns':total_campaigns,'total_leads':total_leads,'credits_remaining':credits_remaining,'all_latest_leads':all_latest_leads,'token':get_token,'all_latest_leads_count':len(all_latest_leads),"aff_data":aff_data})

@login_required(login_url='/users/login/')
@requires_credit
def email_verification(request):
    if request.method == "GET":
        return render(request,'dashboard/single_email_verification.html')

    if request.method == "POST":
        email = request.POST.get('email')

        if email == None or email == "":
            return HttpResponse("invalid_email")

        is_exists = False

        

        #checking the email validity
        get_mx = get_mx_records(email)[-1]

        is_exists = is_valid_email(get_mx,email)

        #end of checking email validity
        
        if is_exists == False:
            sel_user_credit = user_credit.objects.get(user=request.user)
            sel_user_credit.credits_remaining -= 1
            sel_user_credit.save()
           
            return HttpResponse("invalid_email")

        elif is_exists == True:
            if is_valid_email(get_mx,'1'+email) == True:
                return HttpResponse('invalid_email')
            sel_user_credit = user_credit.objects.get(user=request.user)
            sel_user_credit.credits_remaining -= 1
            sel_user_credit.save()
            return HttpResponse("valid_email")

        else:
             return HttpResponse("something_went_wrong")

def email_verification_ext(request):
    

    if request.method == "GET":
        email = request.GET.get('email')

        if email == None or email == "":
            return HttpResponse("invalid_email")

        is_exists = False

        

        #checking the email validity
        get_mx = get_mx_records(email)[-1]

        is_exists = is_valid_email(get_mx,email)

        #end of checking email validity
        
        if is_exists == False:
            #sel_user_credit = user_credit.objects.get(user=request.user)
            #sel_user_credit.credits_remaining -= 1
            #sel_user_credit.save()
           
            return JsonResponse({"status":"invalid_email"})

        elif is_exists == True:
            if is_valid_email(get_mx,'1'+email) == True:
                return HttpResponse('invalid_email')
            #sel_user_credit = user_credit.objects.get(user=request.user)
            #sel_user_credit.credits_remaining -= 1
            #sel_user_credit.save()
            return JsonResponse({"status":"valid_email"})

        else:
             return JsonResponse({"status":"something_went_wrong"})



@login_required(login_url='/users/login/')
@requires_credit
def bulk_email_verification(request):
    if request.method == "GET":
        return render(request,'dashboard/bulk_email_verification.html')

    if request.method == "POST":
        try:
            get_this_user_files = file_uploader.objects.filter(user=request.user)
            for file in get_this_user_files:
                try:
                    os.remove(file.file.path)
                except:
                    pass
                try:
                    os.remove(file.file.path[:-3]+"xlsx")
                except:
                    pass
                file.delete()
        except:
            pass
        get_file = request.FILES.get('file')

        file_instance = file_uploader(user=request.user,file=get_file)


        file_instance.save()

        file_path = file_instance.file.path
        
        #check file extension
        file_extension = file_path.split('.')[-1]


        if file_extension == "xls":
            new_file_path = file_path[:-3]+"xlsx"
            thexls = XLS2XLSX(file_path)
            thexls.to_xlsx(new_file_path)

            information = xlsx_info(new_file_path)


        
        

        elif file_extension == "csv":

            #convert csv to xlsx
            
            check= csv_to_xlsx(file_path,file_instance.file.name)
            new_path = file_instance.file.path[:len(file_instance.file.path)-3]+"xlsx"
            information = xlsx_info(new_path)
           
           # file_instance.file.path=file_instance.file.path[:len(file_instance.file.path)-3]+"xlsx"
            

        elif file_extension == "xlsx":

        
            information = xlsx_info(file_path)

        else:
            os.remove(file_instance.file.path)
            return HttpResponse("invalid_file_extension")

        all_columns = information['column_names']



        return render(request,'dashboard/components/column_selection.html',{'all_columns':all_columns})

           
       

@login_required(login_url='/users/login/')
@csrf_exempt
def bulk_email_verification_result(request):
    if request.method == 'POST':
        get_column_name = request.POST.get('column_name')
        get_file_instance = file_uploader.objects.filter(user=request.user)
        get_file_path = get_file_instance[0].file.path
        actual_file_path = ""
        file_extension = get_file_path.split('.')[-1]

        if file_extension == "xls":
            actual_file_path = get_file_path[:-3]+"xlsx"
           
        elif file_extension == "csv":
            actual_file_path = get_file_path[:-3]+"xlsx"

        elif file_extension == "xlsx":
            actual_file_path = get_file_path
        
        else:
            return HttpResponse("Invalid File")

        information = xlsx_info(actual_file_path)

        all_columns = information['column_names']
        total_columns = information['total_columns']
        total_rows = information['total_rows']

        get_the_email_column_position = all_columns.index(get_column_name)+1
        total_email_verified = 0
        try:
            sel_user_inst = request.user
            sel_user_inst.file_process_percentage = float(0)
            sel_user_inst.save()

        except:
            pass
        for row_num in range(1,total_rows+1):
            try:
                sel_user_inst = request.user
                sel_user_inst.file_process_percentage = float((row_num/total_rows)*100)
                sel_user_inst.save()

                sel_user_credit_inst = user_credit.objects.get(user=request.user)
                if sel_user_credit_inst.credits_remaining == 0:
                    break
                email_val=xlsx_retrive_column_data(row_num,get_the_email_column_position,actual_file_path)
                

                if email_val != None and email_val != "":
                
                    #do email validation here and write the result in the same column
                    if row_num == 1:
                        
                        xlsx_write_on_new_column(row_num,total_columns,"validation status",actual_file_path)

                    else:
                        
                        #checking the email validity
                        try:
                            get_mx = get_mx_records(email_val)[-1]

                            is_exists = is_valid_email(get_mx,email_val)

                        except FunctionTimedOut:
                            is_exists = False
                        
                        if is_exists == True:
                            demo_mail = email_val.split('@')[0]+'doe'+'@'+email_val.split('@')[1]
                            if is_valid_email(get_mx,demo_mail) == True:
                                xlsx_write_on_new_column(row_num,total_columns,"catchall",actual_file_path)
                                total_email_verified += 1
                                sel_user_credit = user_credit.objects.get(user=request.user)
                                sel_user_credit.credits_remaining -= 1
                                sel_user_credit.save()
                            
                            else:
                                xlsx_write_on_new_column(row_num,total_columns,"verified",actual_file_path)
                                total_email_verified += 1
                                sel_user_credit = user_credit.objects.get(user=request.user)
                                sel_user_credit.credits_remaining -= 1
                                sel_user_credit.save()
                        
                        else:
                            total_email_verified += 1
                            sel_user_credit = user_credit.objects.get(user=request.user)
                            sel_user_credit.credits_remaining -= 1
                            sel_user_credit.save()
                            xlsx_write_on_new_column(row_num,total_columns,"email does not exist",actual_file_path)
            
            except:
                pass


                    #end of checking email validity
                   
                    
                     

        
        return render(request,'dashboard/components/show_download_button.html',{'total_verified':total_email_verified})




@login_required(login_url='/users/login/')
def download_bulk_email_verification_file(request):
    get_file_instance = file_uploader.objects.filter(user=request.user)
    get_file_path = get_file_instance[0].file.url
    actual_file_path = ""
    file_extension = get_file_path.split('.')[-1]

    if file_extension == "xls":
        actual_file_path = get_file_path[:-3]+"xlsx"
    
    elif file_extension == "csv":
        actual_file_path = get_file_path[:-3]+"xlsx"
    
    elif file_extension == "xlsx":
        actual_file_path = get_file_path

    else:
        return HttpResponse("Invalid File")
    
    
    return redirect(actual_file_path)


@login_required(login_url='/users/login/')
@requires_credit
def find_email(request):
    if request.method == "GET":
        return render(request,'dashboard/find_email.html')

    if request.method == "POST":
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        domain = request.POST.get('domain')

        #extract only domain name from url
        try:
            domain =domain.split('//')[1]
        except:
            pass
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

        try:

            get_mx = get_mx_records_domain(root_domain)[-1]
        except:
            return render(request,'dashboard/components/found_email.html',{'not_found':True})

        #print('your mx record is:',get_mx)
        for possible_email in possible_combinations:
            try:
                check_valid_or_not = is_valid_email(get_mx,possible_email)
            
            except FunctionTimedOut:
                check_valid_or_not = False

           

            if check_valid_or_not == True:
                print("first found lets check its validity")
                try:
                    demo_mail = possible_email.split('@')[0]+'doe'+'@'+possible_email.split('@')[1]
                    if is_valid_email(get_mx,demo_mail) == True:
                        print("-------yes yes this is a catch all email server --- ----")
                        check_valid_or_not = False
                        sel_user_credit = user_credit.objects.get(user=request.user)
                        sel_user_credit.credits_remaining -= 1
                        sel_user_credit.save()

                        print("----credit deducted 1 for catch all")
                        return render(request,'dashboard/components/found_email.html',{'not_found':True})
                        break
                    sel_user_credit = user_credit.objects.get(user=request.user)
                    sel_user_credit.credits_remaining -= 1
                    sel_user_credit.save()

                    save_lead = leads()
                    save_lead.user = request.user
                    save_lead.first_name = first_name
                    save_lead.last_name = last_name
                    save_lead.email = possible_email.lower()
                    save_lead.website = domain
                    
                    save_lead.save()

                    get_active_campaign = campaigns.objects.get(user=request.user,is_active=True)

                    campaign_leads_inst = campaign_leads()
                    campaign_leads_inst.campaign = get_active_campaign
                    campaign_leads_inst.lead = save_lead
                    campaign_leads_inst.save()
                    
                    print("email found unintentinally ---- not good")
                    return render(request,'dashboard/components/found_email.html',{'email':possible_email.replace(' ','').lower()})
                except:
                    pass
            else:
                pass
        
        print("all loop failed -- finnally going without not found")

        return render(request,'dashboard/components/found_email.html',{'not_found':True})
        



@login_required(login_url='/users/login/')
@requires_credit
def find_bulk_email(request):
    if request.method == "GET":
        return render(request,'dashboard/find_bulk_email.html')

    if request.method == "POST":
        try:
            get_this_user_files = file_uploader.objects.filter(user=request.user)
            for file in get_this_user_files:
                try:
                    os.remove(file.file.path)
                except:
                    pass
                try:
                    os.remove(file.file.path[:-3]+"xlsx")
                except:
                    pass
                file.delete()
        except:
            pass
        
        get_file = request.FILES.get('file')

        file_instance = file_uploader(user=request.user,file=get_file)


        file_instance.save()

        file_path = file_instance.file.path
        
        #check file extension
        file_extension = file_path.split('.')[-1]


        if file_extension == "xls":
            new_file_path = file_path[:-3]+"xlsx"
            thexls = XLS2XLSX(file_path)
            thexls.to_xlsx(new_file_path)

            information = xlsx_info(new_file_path)


        
        

        elif file_extension == "csv":

            #convert csv to xlsx
            
            check= csv_to_xlsx(file_path,file_instance.file.name)
            new_path = file_instance.file.path[:len(file_instance.file.path)-3]+"xlsx"
            information = xlsx_info(new_path)
           
           # file_instance.file.path=file_instance.file.path[:len(file_instance.file.path)-3]+"xlsx"
            

        elif file_extension == "xlsx":

        
            information = xlsx_info(file_path)

        else:
            os.remove(file_instance.file.path)
            return HttpResponse("invalid_file_extension")

        all_columns = information['column_names']



        return render(request,'dashboard/components/email_finder_column_selector.html',{'all_columns':all_columns})





@login_required(login_url='/users/login/')
def find_bulk_email_result(request):
    if request.method == 'POST':
        try:
            get_first_name_column = request.POST.get('first_name_column')
            get_last_name_column = request.POST.get('last_name_column')
            get_domain_column = request.POST.get('website_column')

            get_file_instance = file_uploader.objects.filter(user=request.user)
            get_file_path = get_file_instance[0].file.path
            actual_file_path = ""
            file_extension = get_file_path.split('.')[-1]

            if file_extension == "xls":
                actual_file_path = get_file_path[:-3]+"xlsx"
            
            elif file_extension == "csv":
                actual_file_path = get_file_path[:-3]+"xlsx"

            elif file_extension == "xlsx":
                actual_file_path = get_file_path
            
            else:
                return HttpResponse("Invalid File")

            information = xlsx_info(actual_file_path)

            all_columns = information['column_names']
            total_columns = information['total_columns']
            total_rows = information['total_rows']

            get_the_first_name_column_position = all_columns.index(get_first_name_column)+1
            get_the_last_name_column_position = all_columns.index(get_last_name_column)+1
            get_the_domain_name_column_position = all_columns.index(get_domain_column)+1

            total_email_verified = 0
            try:
                sel_user_inst = request.user
                sel_user_inst.file_process_percentage = float(0)
                sel_user_inst.save()

            except:
                pass

            for row_num in range(1,total_rows+1):
                sel_user_inst = request.user
                sel_user_inst.file_process_percentage = float((row_num/total_rows)*100)
                sel_user_inst.save()

                sel_user_credit = user_credit.objects.get(user=request.user)
                if sel_user_credit.credits_remaining == 0:
                    break
                first_name_val=xlsx_retrive_column_data(row_num,get_the_first_name_column_position,actual_file_path)
                last_name_val=xlsx_retrive_column_data(row_num,get_the_last_name_column_position,actual_file_path)
                domain_val=xlsx_retrive_column_data(row_num,get_the_domain_name_column_position,actual_file_path)
                
                email_found = False
                if first_name_val != None and last_name_val != None and domain_val != None and first_name_val != "" and last_name_val != "" and domain_val != "":
                    try:
                        domain_val = domain_val.split('//')[1]
                    except:
                        continue
                    root_domain_inst = tldextract.extract(domain_val)
                    root_domain = root_domain_inst.domain+'.'+root_domain_inst.suffix

                    possible_combinations = []
                    possible_combinations.append(first_name_val+'@'+root_domain)
                    possible_combinations.append(first_name_val+'.'+last_name_val+'@'+root_domain)
                    
                    possible_combinations.append(last_name_val+'@'+root_domain)

                    possible_combinations.append(last_name_val+'.'+first_name_val+'@'+root_domain)
                    possible_combinations.append(last_name_val+'-'+first_name_val+'@'+root_domain)
                    possible_combinations.append(last_name_val+'_'+first_name_val+'@'+root_domain)
                    possible_combinations.append(first_name_val+'-'+last_name_val+'@'+root_domain)
                    possible_combinations.append(first_name_val+'_'+last_name_val+'@'+root_domain)
                    possible_combinations.append(first_name_val[0]+last_name_val+'@'+root_domain)
                    possible_combinations.append(first_name_val+last_name_val+'@'+root_domain)

                
                    #do email validation here and write the result in the same column
                    if row_num == 1:
                        
                        xlsx_write_on_new_column(row_num,total_columns,"Email",actual_file_path)

                    else:
                        
                        #checking the email validity
                        try:
                            get_mx = get_mx_records_domain(root_domain)[-1]

                        except:
                            continue

                        for comb in possible_combinations:

                            #checking email existance here

                            try:

                                is_exists = is_valid_email(get_mx,comb)

                            except FunctionTimedOut:
                                is_exists = False
                            

                            
                            
                            if is_exists == True:
                                demo_mail=comb.split('@')[0]+'doe'+'@'+comb.split('@')[1]
                                if is_valid_email(get_mx,demo_mail) == True:
                                    is_exists = False
                                    email_found = False
                                    break
                                xlsx_write_on_new_column(row_num,total_columns,comb.lower(),actual_file_path)
                                total_email_verified += 1
                                sel_user_credit = user_credit.objects.get(user=request.user)
                                sel_user_credit.credits_remaining -= 1
                                sel_user_credit.save()
                                email_found = True

                                save_lead = leads()
                                save_lead.user = request.user
                                save_lead.first_name = first_name_val
                                save_lead.last_name = last_name_val
                                save_lead.email = comb.lower()
                                save_lead.website = domain_val
                                
                                save_lead.save()

                                get_active_campaign = campaigns.objects.get(user=request.user,is_active=True)

                                campaign_leads_inst = campaign_leads()
                                campaign_leads_inst.campaign = get_active_campaign
                                campaign_leads_inst.lead = save_lead
                                campaign_leads_inst.save()
                                break
                            
                            else:
                                pass
                        

                        if email_found == False:
                            sel_user_credit = user_credit.objects.get(user=request.user)
                            sel_user_credit.credits_remaining -= 1
                            sel_user_credit.save()
                            xlsx_write_on_new_column(row_num,total_columns,"not found",actual_file_path)



                        #end of checking email validity
                    
        except:
            pass
                     

        
        return render(request,'dashboard/components/show_download_button_bulk_finder.html',{'total_found':total_email_verified})




@login_required(login_url='/users/login/')
def download_bulk_email_found_file(request):

    get_file_instance = file_uploader.objects.filter(user=request.user)
    get_file_path = get_file_instance[0].file.url
    actual_file_path = ""
    file_extension = get_file_path.split('.')[-1]

    if file_extension == "xls":
        actual_file_path = get_file_path[:-3]+"xlsx"
    
    elif file_extension == "csv":
        actual_file_path = get_file_path[:-3]+"xlsx"
    
    elif file_extension == "xlsx":
        actual_file_path = get_file_path

    else:
        return HttpResponse("Invalid File")
    
    
    return redirect(actual_file_path)




#author email finding functionality starts here


@login_required(login_url='/users/login/')
@requires_credit
def find_author_email(request):
    if request.method == "GET":
        return render(request,'dashboard/find_author_email.html')

    if request.method == "POST":


        names = []
        domain = request.POST.get('domain')

        print('domain name is ',domain)

        if domain == "" or domain == None or domain == " ":
            return HttpResponse("Please enter a valid blog post url")

        else:
            call_author = get_author_name(domain)
            author_name = call_author["string"]
            source_code = call_author["source_code"]

            print("first try author name is - ",author_name)

            pattern = re.compile(r"\w+")

            split_author_name = pattern.findall(author_name)

            try:
                if len(split_author_name) == 1 and split_author_name[0] != None:

                    names.append(split_author_name[0])
                    
                elif len(split_author_name) == 2:
                    names= names + split_author_name

                elif len(split_author_name) == 3:
                    names = names + split_author_name

                else:
                    pass
                    
            except:
                return render(request,'dashboard/components/found_email.html',{'not_found':True})

            for i,name in enumerate(names):
                if name == None or name == " " or name=="" or name == "None":
                    del names[i]




            #checking firstname and lastname availability and trying AI based approach
            print("names are - ",names)
            if len(names) == 0 or names == None:
                try:
                    get_list_of_names = get_author_name_extracting_attribute(domain,source_code)

                    print("get list of names ",get_list_of_names)
                    new_names_cleaned = []
                    for item in get_list_of_names:
                        if item != None or item != "" or item != " ":
                            if "\n" in item:
                                item = item.split("\n")
                                new_names_cleaned.append(item[-1].strip())
                            
                            else:
                                new_names_cleaned.append(item.strip())
                    
                    get_list_of_names = new_names_cleaned

                    print("after cleaning get list of names ",get_list_of_names)

                    

                    if get_list_of_names != None and len(get_list_of_names) > 0:
                        names = get_list_of_names
                        


                        #return render(request,'dashboard/components/found_email.html',{'not_found':True})

                except:
                    pass

        #extract only domain name from url

        #print('firstname is from second ',first_name,' lastname is ',last_name,' domain is ',domain)
        try:
            domain = domain.split('//')[1]
        except:
            pass

        

        #iterate through all the names and find emails

        
        for name in names:
            print("name is in loop ",name)

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

            print(' after fname ',first_name,' after lname ',last_name,' dmain ',domain)

            if first_name != None and last_name != None:
                try:
                    found_email = return_email_found_status(first_name,last_name,domain)
                except:
                    found_email = None
                
                if found_email != None:

                    


                    
                    try:
                        if return_email_found_status(first_name+'1',last_name+'1',domain) != None:
                            found_email = None
                            print("email is catch all sorry -- ")
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
                    save_lead.website = domain
                    #save_lead.position = get_position
                    save_lead.save()

                    get_active_campaign = campaigns.objects.get(user=request.user,is_active=True)

                    campaign_leads_inst = campaign_leads()
                    campaign_leads_inst.campaign = get_active_campaign
                    campaign_leads_inst.lead = save_lead
                    campaign_leads_inst.save()

                    
                    return render(request,'dashboard/components/found_email.html',{'email':found_email,'position':None,'first_name':first_name,'last_name':last_name})
                else:
                    pass
            
            
        try:
            if found_email == None:    
        
                sel_user_credit = user_credit.objects.get(user=request.user)
                sel_user_credit.credits_remaining -= 1
                sel_user_credit.save()
                return render(request,'dashboard/components/found_email.html',{'not_found':True})

        except:
            return render(request,'dashboard/components/found_email.html',{'not_found':True})
            





        

        return render(request,'dashboard/components/found_email.html',{'not_found':True})
        





#bulk author finder starts here


def bulk_author_leads(request):
    if request.method == "GET":
        
        curr_sub = subscription_data.objects.get(user=request.user)
        curr_sub_plan = curr_sub.package.name
        
        plan = None

        if curr_sub_plan == "FREE" or curr_sub_plan == "free":
            plan = "FREE"
        

        return render(request, 'dashboard/bulk_author_leads.html',{'plan':plan})

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

            return render(request,'dashboard/components/column_selector.html',{'all_columns':headers})

            





        except:
            return HttpResponse("Something Went Wrong ! Please Try Again")


        


def bulk_author_leads_results(request):
    if request.method == "GET":
        return HttpResponse("Request method not allowed")

    if request.method == "POST":
        get_all_the_uploaded_files = lead_file.objects.filter(uploaded_by=request.user)

        the_last_file = get_all_the_uploaded_files.last()
        total_found = 0
        domain_column = request.POST.get('website_column')
        #job_position = request.POST.get('job_position')

        headers = None
        data = None

        if domain_column != None:
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
                found_email = None

                sel_user_inst = request.user
                sel_user_inst.file_process_percentage = float((i/len(data))*100)
                sel_user_inst.save()
               

                i+=1

                names = []
                domain = domain_column

                print('domain name is ',dt[domain])

                if dt[domain] == "" or dt[domain] == None or dt[domain] == " ":
                    return HttpResponse("Please enter a valid blog post url")

                else:
                    call_author = get_author_name(dt[domain])
                    author_name = call_author["string"]
                    source_code = call_author["source_code"]

                    #print("source code is - ",source_code)

                    print("first try author name is - ",author_name)

                    pattern = re.compile(r"\w+")

                    print("author name is - ",author_name)

                    try:
                        split_author_name = pattern.findall(author_name)
                    except:
                        author_name = None

                    try:
                        if len(split_author_name) == 1 and split_author_name[0] != None:

                            names.append(split_author_name[0])
                            
                        elif len(split_author_name) == 2:
                            names= names + split_author_name

                        elif len(split_author_name) == 3:
                            names = names + split_author_name

                        else:
                            pass
                            
                    except:
                        pass

                    for i,name in enumerate(names):
                        if name == None or name == " " or name=="" or name == "None":
                            del names[i]




                    #checking firstname and lastname availability and trying AI based approach
                    print("names are - ",names)
                    if len(names) == 0 or names == None:
                        try:
                            get_list_of_names = get_author_name_extracting_attribute(dt[domain],source_code)

                            print("get list of names ",get_list_of_names)
                            new_names_cleaned = []
                            for item in get_list_of_names:
                                if item != None or item != "" or item != " ":
                                    if "\n" in item:
                                        item = item.split("\n")
                                        new_names_cleaned.append(item[-1].strip())
                                    
                                    else:
                                        new_names_cleaned.append(item.strip())
                            
                            get_list_of_names = new_names_cleaned

                            print("after cleaning get list of names ",get_list_of_names)

                            

                            if get_list_of_names != None and len(get_list_of_names) > 0:
                                names = get_list_of_names
                                names = names[::-1]
                                


                                #return render(request,'dashboard/components/found_email.html',{'not_found':True})

                        except:
                            pass

                #extract only domain name from url

                #print('firstname is from second ',first_name,' lastname is ',last_name,' domain is ',domain)
                try:
                    dt[domain] = dt[domain].split('//')[1]
                except:
                    pass

                #check if  the user has enough credits or not
                select_user_credit = user_credit.objects.get(user=request.user)
                if select_user_credit.credits_remaining < 5:
                    break

                
                
                

                for name in names:
                    print("the name is --------- ",name)

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
                        
                    if first_name != None and last_name != None:
                        try:
                            found_email = return_email_found_status(first_name,last_name,dt[domain])
                            
                        except:
                            found_email = None

                            
                            
                            
                        if found_email != None:

                                
                            try:
                                if return_email_found_status(first_name+'1',last_name+'1',dt[domain]) != None:
                                    found_email = None
                                    print("catch all found")
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
                           # save_lead.position = job_position
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



@csrf_exempt
def contact_us(request):
    name = request.POST.get('name')
    email = request.POST.get('email')
    message = request.POST.get('message')
    subject = request.POST.get('subject')

    contact.objects.create(name=name,email=email,message=message,subject=subject)

    return JsonResponse({'status':'ok'})
