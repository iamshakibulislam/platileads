from turtle import update
from django.shortcuts import render,redirect
from django.http import HttpResponse,JsonResponse
#import django messages
from django.contrib import messages
import re
from .models import *
from .forms import *
import pandas as pd
import time
import json
import os
import random
from PIL import Image
from datetime import datetime,date
import string
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .cron import *
from django.db.models import Q,Sum,Count,Max

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



def contacts_book(request):
    sel_cam=contact_campaign.objects.filter(user=request.user)
    
    

    page = request.GET.get('page', 1)

    paginator = Paginator(sel_cam, 10)

    try:
        stats = paginator.page(page)
    except PageNotAnInteger:
        stats = paginator.page(1)
    except EmptyPage:
        stats = paginator.page(paginator.num_pages)

    #return render(request,'email_sending/sender_list.html',{'stats':stats,'lenth_of_stats':len(stats)})

    

    for x in stats:
        total_contacts=len(contact_list.objects.filter(contact_campaign=x))
        setattr(x,"contacts_total",total_contacts)


    
    return render(request,'email_sending/contacts_book.html',{'inf':stats,'total_dt':len(stats)})




def delete_contact_book(request):
    if request.method == "POST":
        contact_book_id=request.POST.get("id",0)
        
        if contact_book_id == 0 or contact_book_id == None:
            messages.info(request,"Wrong contact book selected !")
            return redirect(request.META["HTTP_REFERER"])

        else:
            sel_contact_book = contact_campaign.objects.get(id=contact_book_id)
            sel_contact_book.delete()
            messages.info(request,f"Contact book ({sel_contact_book.name}) deleted !")
            return redirect(request.META["HTTP_REFERER"])
    else:
        messages.info(request,"wrong request !")
        return redirect(request.META["HTTP_REFERER"])


def get_contacts(request):
    get_cam_id = request.GET.get('id',0)
    if get_cam_id == 0 or get_cam_id == None:
        messages.info(request,"wrong contact book selected !")
        return redirect(request.META["HTTP_REFERER"])

    contact_listing = contact_list.objects.filter(contact_campaign = contact_campaign.objects.get(id=get_cam_id) )

    page = request.GET.get('page', 1)

    paginator = Paginator(contact_listing, 10)

    try:
        stats = paginator.page(page)
    except PageNotAnInteger:
        stats = paginator.page(1)
    except EmptyPage:
        stats = paginator.page(paginator.num_pages)

    return render(request,'email_sending/contacts_list.html',{'inf':stats,'total_dt':len(stats),'cam_id':get_cam_id,'contact_book':contact_campaign.objects.get(id=get_cam_id)})




def delete_contact(request):
    if request.method == "POST":
        contact_id=request.POST.get("id",0)
        
        if contact_id == 0 or contact_id == None:
            messages.info(request,"Wrong contact  selected !")
            return redirect(request.META["HTTP_REFERER"])

        else:
            sel_contact = contact_list.objects.get(id=contact_id)
            sel_contact.delete()
            messages.info(request,"Contact  deleted !")
            return redirect(request.META["HTTP_REFERER"])
    else:
        messages.info(request,"request error !")
        return redirect(request.META["HTTP_REFERER"])




def email_campaign(request):
    if request.method == "GET":
        form = messageForm()
        
        
        cont_camp = contact_campaign.objects.filter(user=request.user)
        sender_email = emails_for_campaign.objects.filter(user=request.user)
        return render(request,"email_sending/email_campaign.html",{'form':form,'cont_camp':cont_camp,'sender_emails':sender_email})



def render_followup(request):

    

    letters = string.ascii_lowercase

    randstr = ''.join(random.choice(letters) for i in range(7))

    followup_form = getFollowupForm(randstr)

    followno = request.GET.get("followno",1)

    return render(request,"email_sending/components/render_followup.html",{'followup_form':followup_form,'randstr':"id_"+randstr,"follow_no":followno})



def save_campaign(request):
    if request.method == "GET":
        return HttpResponse("not allowed")


    if request.method == "POST":
        dt=json.loads(request.POST["datas"])
        sel_email = emails_for_campaign.objects.get(id=int(dt["sender_email"]),user=request.user)
        
        sel_contact_book = contact_campaign.objects.get(id=int(dt["contact_book"]))
        create_camp=sending_campaigns.objects.create(campaign_name=dt["campaign"],email=sel_email,contact_book=sel_contact_book)

        for data in dt["data"]:
            email_messages.objects.create(campaign=create_camp,subject=dt["subject"],message=data["message"],delivery_date=data["delivery_date"])
        


        return JsonResponse({'status':'ok'})



#create a blank image for tracking email openings


def blank_image(request):
    cam_id = request.GET.get('camp')
    cont_id = request.GET.get('cont_id',0)

    
    try:
        sel_camp = sending_campaigns.objects.get(id=int(cam_id))
        sel_cont = contact_list.objects.get(id=int(cont_id))

    except:
        sel_camp =0
        cont_id=0

    try:
        check_track = sending_track.objects.get(campaign=sel_camp,sent_to=sel_cont)
    except:
        check_track = sending_track.objects.create(campaign=sel_camp,sent_to=sel_cont)

    try:

        if sel_camp !=0 and check_track.is_opened == False:
        
            sel_track=sending_campaign_track.objects.get(campaign=sel_camp)
            sel_track.opened_total +=1
            
            sel_track.save()

            try:

                update_sending=sending_track.objects.get(sent_to=sel_cont,campaign=sel_camp)
                update_sending.is_opened = True
                update_sending.save()
            except:
                sending_track.objects.create(sent_to=sel_cont,campaign=sel_camp,is_opened=True)

    except sending_campaign_track.DoesNotExist:
        sending_campaign_track.objects.create(campaign=sel_camp,opened_total=1)




    print('cam id is ',cam_id)
    print("\nImage Loaded\n")
    red = Image.new('RGB', (1, 1))
    response = HttpResponse(content_type="image/png")
    red.save(response, "PNG")
    return response




def test_email_send(request):
    #check_reply()
    send_email_campaign()

    return HttpResponse("status ok")



def campaigns(request):
    dt=[]
    sel_all_camp = sending_campaigns.objects.filter(email__user=request.user)

    for camp in sel_all_camp:
        get_messages=email_messages.objects.filter(campaign=camp)
        mx = get_messages.aggregate(Max('delivery_date'))['delivery_date__max']
        followup_total = len(get_messages)-1
        

        if date(mx.year,mx.month,mx.day) < datetime.now().date():
            camp.is_active = False
            camp.is_expired = True
            camp.save()

        
        try:
            trk=sending_campaign_track.objects.get(campaign=camp)
        except sending_campaign_track.DoesNotExist:
            trk=sending_campaign_track.objects.create(campaign=camp)

        contacts_total = len(contact_list.objects.filter(contact_campaign=camp.contact_book))
        
        

        
        dt.append({'id':camp.id,'is_active':camp.is_active,'name':camp.campaign_name,'start':camp.created_at,
        'followup':followup_total,
        'contacts_total':contacts_total,'total_sent':trk.total_sent,'opened_total':trk.opened_total,
        'replied_total':trk.replied_total,'is_active':camp.is_active,
        'opened_perc':round(((trk.opened_total*100)/contacts_total),2),'replied_perc':round(((trk.replied_total*100)/contacts_total),2),'is_expired':camp.is_expired})

    dt=dt[::-1]
    page = request.GET.get('page', 1)

    paginator = Paginator(dt, 10)

    try:
        stats = paginator.page(page)
    except PageNotAnInteger:
        stats = paginator.page(1)
    except EmptyPage:
        stats = paginator.page(paginator.num_pages)

    return render(request,'email_sending/email_campaigns.html',{'stats':stats,'length_of_stats':len(stats)})




def change_campaign_status(request):
    if request.method == 'POST':
        try:
            campaign = sending_campaigns.objects.get(id=request.POST['campaign_id'])

            get_messages=email_messages.objects.filter(campaign=campaign)
            mx = get_messages.aggregate(Max('delivery_date'))['delivery_date__max']
            
            

            if date(mx.year,mx.month,mx.day) < datetime.now().date():
                campaign.is_active = False
                campaign.is_expired = True
                campaign.save()

                messages.info(request,"Campaign has expired !")

                return redirect(request.META["HTTP_REFERER"])

            if campaign.is_active == True:
                campaign.is_active = False
                campaign.save()
            else:
                
                campaign.is_active = True
                campaign.save()

            messages.info(request,"Status Updated !")

            return redirect(request.META["HTTP_REFERER"])

        except:
            return redirect(request.META['HTTP_REFERER'])
