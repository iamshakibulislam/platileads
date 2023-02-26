from webbrowser import get
from django.shortcuts import render
from datetime import datetime,timedelta
from django.conf import settings



def backlink_builder(request):
    return render(request,"home/backlink_builder_vsl.html")


def home_page(request):
    if request.method == "GET":
        lifetime_payment_link  = settings.STRIPE_LIFETIME_PAYMENT_LINK
        try:
            get_cookie_ref = 0
            print("your cookie si ",request.COOKIES["ref"])
            if request.COOKIES.get('ref') != None:
                get_cookie_ref = request.COOKIES.get('ref')
                if get_cookie_ref != None:
                    lifetime_payment_link = lifetime_payment_link+"/?client_reference_id="+get_cookie_ref
                    render_the_page=render(request,'home/index.html',{'lifetime_payment_link':lifetime_payment_link})
        
        except:
            get_cookie_ref = None

        
        
        try:
            try:
                get_ref_id = request.GET['ref']
                del request.COOKIES['ref']
                lifetime_payment_link = settings.STRIPE_LIFETIME_PAYMENT_LINK
                lifetime_payment_link = lifetime_payment_link+"/?client_reference_id="+get_ref_id
                render_the_page=render(request,'home/index.html',{'lifetime_payment_link':lifetime_payment_link})


            except:
                pass

            render_the_page=render(request,'home/index.html',{'lifetime_payment_link':lifetime_payment_link})
            get_ref_id = request.GET['ref']
            if get_ref_id != "" or get_ref_id != None:
                #create a django cookie with key ref and value of get_ref_id set expire for 30 days and expire after 30 days for whole domain
                
                render_the_page.set_cookie('ref', get_ref_id,max_age=2592000, expires=datetime.now() + timedelta(days=30), path='/' ,httponly=False)

            


                
                
        except:
            pass

        print("ki ihocce ", request.COOKIES.get('ref'))
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