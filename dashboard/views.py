#from http.client import HTTPResponse
from logging import root
from django.shortcuts import render,redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from time import sleep

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
from .custom_scripts import get_mx_records,get_mx_records_domain,is_valid_email,xlsx_info,xlsx_write_on_new_column,xlsx_retrive_column_data,csv_to_xlsx,requires_credit
from .models import *
from func_timeout import *



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
                            if is_valid_email(get_mx,'1'+email_val) == True:
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
                if is_valid_email(get_mx,'1'+possible_email) == True:
                    break
                sel_user_credit = user_credit.objects.get(user=request.user)
                sel_user_credit.credits_remaining -= 1
                sel_user_credit.save()

                save_lead = leads()
                save_lead.user = request.user
                save_lead.first_name = first_name
                save_lead.last_name = last_name
                save_lead.email = possible_email
                save_lead.website = domain
                
                save_lead.save()

                get_active_campaign = campaigns.objects.get(user=request.user,is_active=True)

                campaign_leads_inst = campaign_leads()
                campaign_leads_inst.campaign = get_active_campaign
                campaign_leads_inst.lead = save_lead
                campaign_leads_inst.save()
                
                return render(request,'dashboard/components/found_email.html',{'email':possible_email.replace(' ','')})
            
            else:
                pass

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

                    except FunctionTimedOut:
                        pass

                    for comb in possible_combinations:

                        #checking email existance here

                        try:

                            is_exists = is_valid_email(get_mx,comb)

                        except FunctionTimedOut:
                            is_exists = False
                        

                        
                        
                        if is_exists == True:
                            if is_valid_email(get_mx,'1'+comb) == True:
                                is_exists = False
                                break
                            xlsx_write_on_new_column(row_num,total_columns,comb,actual_file_path)
                            total_email_verified += 1
                            sel_user_credit = user_credit.objects.get(user=request.user)
                            sel_user_credit.credits_remaining -= 1
                            sel_user_credit.save()
                            email_found = True

                            save_lead = leads()
                            save_lead.user = request.user
                            save_lead.first_name = first_name_val
                            save_lead.last_name = last_name_val
                            save_lead.email = comb
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




@csrf_exempt
def contact_us(request):
    name = request.POST.get('name')
    email = request.POST.get('email')
    message = request.POST.get('message')
    subject = request.POST.get('subject')

    contact.objects.create(name=name,email=email,message=message,subject=subject)

    return JsonResponse({'status':'ok'})
