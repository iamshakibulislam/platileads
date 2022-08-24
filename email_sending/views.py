from django.shortcuts import render,redirect
from django.http import HttpResponse,JsonResponse
#import django messages
from django.contrib import messages
import re
from .models import *
import pandas as pd
import time
import os

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def add_campaign_email(request):
    if request.method == "GET":
        return render(request,'email_sending/add_email_for_cam.html')

    if request.method == "POST":
        email = request.POST.get('email')
        app_password = request.POST.get('app_password')
        provider = request.POST.get('provider')

        if email != None and app_password != None and provider != None:
            emails_for_campaign.objects.create(user=request.user,email=email,app_password=app_password,provider=provider)
            return render(request,'email_sending/components/email_added.html',{'status':'success','email':email})



def sender_list(request):
    if request.method == "GET":
        stats_all = emails_for_campaign.objects.filter(user=request.user).order_by('-id')
        
        page = request.GET.get('page', 1)

        paginator = Paginator(stats_all, 10)

        try:
            stats = paginator.page(page)
        except PageNotAnInteger:
            stats = paginator.page(1)
        except EmptyPage:
            stats = paginator.page(paginator.num_pages)

        return render(request,'email_sending/sender_list.html',{'stats':stats,'lenth_of_stats':len(stats)})


    if request.method == "POST":
        identity = request.POST.get('sender_id',0)
        if int(identity)!=0 and request.user == emails_for_campaign.objects.get(id=identity).user:
            emails_for_campaign.objects.filter(id=identity).delete()
            messages.success(request,'Sender email deleted successfully !')
            return redirect('sender_list')

        else:
            messages.info(request,'Something went wrong !')
            return redirect('sender_list')



def upload_contacts(request):
    if request.method == "GET":
        return render(request,"email_sending/contact_uploader.html")

    if request.method == "POST":
        get_file = request.FILES['file']

        if get_file.name.split('.')[-1] != 'csv':
            return HttpResponse("Invalid file")

        try:
            all_files = uploaded_files.objects.filter(user=request.user)
            for f in all_files:
                try:
                    os.remove(f.file.path)
                    f.delete() 
                except:
                    pass  

        except:
            pass         

        up_file=uploaded_files.objects.create(user=request.user,file=get_file)
        

        df=pd.read_csv(up_file.file.path)
        df.fillna(" ",inplace=True)

        cols = df.columns.to_list()  #should be passed to template as select option values

        filter_fieldnames = ["id","created_at","updated_at","contact_campaign","date"]

        fields = contact_list._meta._get_fields()

        db_fields = []   #should be passed to template as select option name

        for field in fields:
            if field.name not in filter_fieldnames:
                db_fields.append(field.name)
            
            else:
                pass


       


        samble_data = []

        for i,row in df.iterrows():
            
            row = dict(row)
            samble_data.append(list(row.values()))
            if i > 8:
                break

        #print(cols," and db fields are ",db_fields," and samble data are ",samble_data)

        return render(request,'email_sending/components/select_column.html',{'cols':cols,'db_fields':db_fields,'samble_data':samble_data})



def process_contacts(request):
    if request.method == "GET":
        return HttpResponse("not allowed")

    if request.method == "POST":
        file_path = uploaded_files.objects.filter(user=request.user).last()

        df = pd.read_csv(file_path.file.path)
        contact_list_name = request.POST.get('list_name','default')
        crt_contact_camp=contact_campaign.objects.create(user=request.user,name=contact_list_name)
        for item in request.POST:
            #print(item," -->> ",request.POST.get(item))

            #rename the columns of the csv file
            
            try:
                df.rename(columns={request.POST.get(item):item}, inplace=True)
                
            except:
                pass
        

       

        #here loop through all the rows and save the contact data into contact list
        
        all_rows = len(df.index)

        request.user.file_process_percentage = 0
        request.user.save()

        counter = 0
        for i,cont in df.iterrows():
            counter +=1
            try:
                request.user.file_process_percentage =round((counter*100)/all_rows,2)
                request.user.save()
                #time.sleep(3)
                lst_cont_inst = contact_list()
                lst_cont_inst.contact_campaign = crt_contact_camp
                obj = dict(cont)
                for key,value in obj.items():
                    try:
                        setattr(lst_cont_inst,key,value)
                    except:
                        pass

                lst_cont_inst.save()
            
            except:
                pass

           


        return render(request,"email_sending/components/contacts_added.html",{'contact_book':contact_list_name,'status':'success','total':counter})