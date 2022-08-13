from cmath import pi
from django.shortcuts import render,redirect
from django.http import HttpResponse,JsonResponse
import smtplib
import email.mime.multipart
from email.mime.text import MIMEText
from imap_tools import *
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import re
from PIL import Image

from .models import *
from .cronjob import *
from .custom_func import *
from users.models import *
from django.conf import settings as st
from datetime import datetime,timedelta
#import django messages
from django.contrib import messages
import openai
from .tests import *

openai.api_key = st.OPENAI_API_KEY

def test_email_connection(request):
    

    if request.method == "GET":
        email = request.GET.get('email')
        app_password = request.GET.get('app_password')
        if test_email_connection_status(email,app_password):
            return JsonResponse({'status':'success'})
        else:
            return JsonResponse({'status':'fail'})


def add_email(request):
    if request.method == "GET":
        return render(request,'warmup/add_email.html')

    if request.method == "POST":
        email = request.POST.get('email')
        provider = request.POST.get('provider')
        app_password = request.POST.get('app_password')
        start_count = request.POST.get('start')
        increament = request.POST.get('increament')
        stop = request.POST.get('stop')

        print(email,provider,app_password,start_count,increament,stop)

        new_warmup=warmup_campaign.objects.create(
            user=request.user,
            email=email,
            app_password=app_password.strip(),
            start_count=start_count,
            increament_count=increament,
            end_at=stop,
            provider=provider.lower()
        )

        warmup_track.objects.create(
            campaign=new_warmup,
            total_sent=0,
            today_sent=0,
            spam_count=0,
            moved_to_inbox=0


        )



        return render(request,'warmup/components/email_added.html',{'status':'success','email':email})




def warmup_stats(request):
    if request.method == "GET":
        stats_all = warmup_track.objects.filter(campaign__user=request.user).order_by('-id')
        
        page = request.GET.get('page', 1)

        paginator = Paginator(stats_all, 10)

        try:
            stats = paginator.page(page)
        except PageNotAnInteger:
            stats = paginator.page(1)
        except EmptyPage:
            stats = paginator.page(paginator.num_pages)

        return render(request,'warmup/warmup_stats.html',{'stats':stats,'lenth_of_stats':len(stats)})

    
    if request.method == "POST":
        stat_id = request.POST.get('stat_id')
        stat_sel = warmup_track.objects.get(id=int(stat_id))
        prev_url=request.META.get('HTTP_REFERER')

        sel_campaign = stat_sel.campaign

        if datetime.now().date() <= sel_campaign.end_at:

            if sel_campaign.is_active == True:
                sel_campaign.is_active = False
                sel_campaign.save()
                messages.error(request,'Campaign paused  !')

            else:
                sel_campaign.is_active = True
                sel_campaign.save()
                messages.success(request,'Campaign resumed  !')

        else:
            messages.error(request,'Campaign has been expired !')


        return redirect(prev_url)




def testimage(request):
    cam_id = request.GET.get('id')
    print('cam id is ',cam_id)
    print("\nImage Loaded\n")
    red = Image.new('RGB', (1, 1))
    response = HttpResponse(content_type="image/png")
    red.save(response, "PNG")
    return response
   # return redirect('/static/base_images/email_warmup.png')