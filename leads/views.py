from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from .models import *
from django.http import HttpResponse, JsonResponse
from xls2xlsx import XLS2XLSX
from openpyxl import load_workbook,Workbook
import smtplib
import csv
import tldextract
from users.models import *
from django.views.decorators.csrf import csrf_exempt
from dashboard.custom_scripts import get_mx_records,get_mx_records_domain,is_valid_email,xlsx_info,xlsx_write_on_new_column,xlsx_retrive_column_data,csv_to_xlsx,xlsx_create_and_write
import os
import json



@login_required(login_url='users/login/')
def create_campaign(request):
    if request.method == "POST":
        name = request.POST.get('name')
        description = request.POST.get('description')
        get_all_camp = campaigns.objects.filter(user=request.user)
        is_active =  False

        if len(get_all_camp) == 0:
            is_active = True
        campaigns.objects.create(user=request.user,name=name,description=description,is_active=is_active)
        return HttpResponse("<div class='alert alert-success' style='width:36rem'>Campaign created successfully</div>")



@login_required(login_url='users/login/')
def campaign_list(request):
    get_all_camp = campaigns.objects.filter(user=request.user).order_by('id')

    all_leads_for_this_campaign = []

    for camp in get_all_camp:
        sel_lead_total = len(campaign_leads.objects.filter(campaign=camp))
        all_leads_for_this_campaign.append({'id':camp.id,'name':camp.name,'description':camp.description,'is_active':camp.is_active,'date':camp.date,'leads_total':sel_lead_total})
    return render(request,'leads/campaign_list.html',{'get_all_camp':all_leads_for_this_campaign})



@login_required(login_url='/users/login/')
def delete_campaign(request):
    if request.method == "POST":
        try:
            camp_id = request.POST.get('camp_id')
            camp = campaigns.objects.get(id=camp_id)
            camp.delete()
            return HttpResponse("<div class='alert alert-success' style='width:36rem'>Campaign deleted successfully</div>")
        except:
            return HttpResponse("<div class='alert alert-danger' style='width:36rem'>Something went wrong</div>")

    else:
        return HttpResponse("<div class='alert alert-danger' style='width:36rem'>Sorry ! Something is not right ! Try again later</div>")



@login_required(login_url='/users/login/')
def show_leads(request,pk):
    sel_camp = campaigns.objects.get(id=pk,user=request.user)
    sel_leads = campaign_leads.objects.filter(campaign=sel_camp)

    return render(request,'leads/lead_list.html',{'get_all_leads':sel_leads,'campaign_name':sel_camp.name,'campaign_id':sel_camp.id})
    


@login_required(login_url='/users/login/')
def delete_lead(request):
    if request.method == "POST":
        try:
            lead_id = request.POST.get('lead_id')
            lead = campaign_leads.objects.get(id=lead_id)
            lead.delete()
            return HttpResponse("<div class='alert alert-success' style='width:36rem'>Lead deleted successfully</div>")
        except:
            return HttpResponse("<div class='alert alert-danger' style='width:36rem'>Something went wrong</div>")

    else:
        return HttpResponse("<div class='alert alert-danger' style='width:36rem'>Sorry ! Something is not right ! Try again later</div>")


@login_required(login_url='/users/login/')
def export_lead(request,pk):
   
    sel_camp = campaigns.objects.get(id=pk,user=request.user)
    sel_leads = campaign_leads.objects.filter(campaign=sel_camp)

    try:
        dir_name = "media/export/"
        listing_dir = os.listdir(dir_name)

        for item in listing_dir:
            if item.endswith(str(request.user.id)+".xlsx"):
                os.remove(os.path.join(dir_name, item))
               

    except:
        pass

    filepath = 'media/export/'+str(sel_camp.name)+str(request.user.id)+'.xlsx'

    all_rows = []
    columns_header = ['first name','last name','email','company','website','linkedin','position','location','employee total','industry']

    for lead in sel_leads:
        all_rows.append([lead.lead.first_name,lead.lead.last_name,lead.lead.email,lead.lead.company,lead.lead.website,lead.lead.linkedin_profile,lead.lead.position,lead.lead.location,lead.lead.employee_total,lead.lead.industry])

    writing_to_xls=xlsx_create_and_write(filepath,all_rows,columns_header)

    if writing_to_xls == True:
        return redirect('/media/export/'+str(sel_camp.name)+str(request.user.id)+'.xlsx')

    else:
        return HttpResponse("<div class='alert alert-danger' style='width:36rem'>Sorry ! Something is not right ! Try again later</div>")

        
    

@login_required(login_url='/users/login/')
def activate_campaign(request):

    if request.method == "GET":
        sel_active_camp = campaigns.objects.filter(user=request.user,is_active=True).first()
        sel_all_campaigns = campaigns.objects.filter(user=request.user)
        return render(request,'leads/activate_campaign.html',{'active_campaign':sel_active_camp,'campaigns':sel_all_campaigns})

    if request.method == "POST":
        get_camp_id = request.POST['campaign']
        get_camp = campaigns.objects.get(id=get_camp_id)
        
        get_all_camp = campaigns.objects.filter(user=request.user)

        for x in get_all_camp:
            x.is_active = False
            x.save()
        
        get_camp.is_active = True

        get_camp.save()

        return redirect('activate_campaign')



@csrf_exempt
def capture_leads(request):
    if request.method == "GET":
        return JsonResponse({'status':'not allowed'})

    if request.method == "POST":
       
        
        data = request.POST
        
        get_token = data['plati_token']

        if get_token == '' or get_token == None:

            return JsonResponse({'status':'not authenticated yet !'})

        else:
            try:
                get_user = User.objects.get(secret_id=get_token)
                
            
            except:
                return JsonResponse({'status':'not authenticated'})

        if campaigns.objects.filter(user=get_user,is_active=True).count() == 0:
            return JsonResponse({'status':'no active campaign'})

        first_name = data['first_name']
        last_name = data['last_name']
        
        company = data['company']
        website = data['website']
        linkedin_profile = data['linkedin_profile']
        position = data['position']
        phone = data.get('phone')
        location = data['location']
        employee_total = data['employee_total']
        industry = data['industry']

        is_found = False


        if phone == "" or phone == None:
            phone = "N/A"

        print('fname',first_name,'lname',last_name,'com',company,'web',website,'linkedin',linkedin_profile,'pos',position,'phone',phone,'industry',industry,'location',location,'employee_total',employee_total)

        sel_camp = campaigns.objects.filter(user=get_user,is_active=True).first()

       

        try:
            root_domain_inst = tldextract.extract(website)
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
                    
                    #save the lead into db with active campaign
                    sel_cred=user_credit.objects.get(user=get_user)
                    if sel_cred.credits_remaining == 0:
                        return JsonResponse({'status':'not enough credits'})
                    
                    else:
                        sel_cred.credits_remaining = sel_credit.credits_remaining - 1
                        sel_cred.save()
                        is_found = True

                    lead_create = leads.objects.create(first_name=first_name,last_name=last_name,email=possible_email,company=company,website=website,linkedin_profile=linkedin_profile,position=position,location=location,employee_total=employee_total,industry=industry)

                    campaign_leads.objects.create(lead=lead_create,campaign=sel_camp)

                    return JsonResponse({'email':possible_email,'status':'success'})
                
                else:
                    pass
            
            if is_found == False:
                return JsonResponse({'status':'not found'})

        except:
            return JsonResponse({'status':'error'})



        

           

