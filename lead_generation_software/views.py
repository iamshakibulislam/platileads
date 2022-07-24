from django.shortcuts import render
from datetime import datetime,timedelta

def home_page(request):
    if request.method == "GET":
        render_the_page=render(request,'home/index.html')
        try:
            get_ref_id = request.GET['ref']
            if get_ref_id != "" or get_ref_id != None:
                #create a django cookie with key ref and value of get_ref_id set expire for 30 days and expire after 30 days for whole domain
                
                render_the_page.set_cookie('ref', get_ref_id,max_age=2592000, expires=datetime.now() + timedelta(days=30), path='/' ,httponly=False)
                
                
        except:
            pass

        return render_the_page
        


def about_us(request):
    if request.method == "GET":
        return render(request,'home/about-us.html')


def terms_and_conditions(request):
    if request.method == "GET":
        return render(request,'home/terms_and_conditions.html')

def privacy_policy(request):
    if request.method == "GET":
        return render(request,'home/privacy-policy.html')

def affiliates(request):
    if request.method == "GET":
        return render(request,'home/affiliates.html')