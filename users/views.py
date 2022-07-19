from django.shortcuts import render,redirect
from django.http import HttpResponse, JsonResponse
from users.models import *
from time import sleep
from django.contrib import auth
from subscriptions.models import packages,subscription_data
#import django messages
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import datetime
from datetime import timedelta
from leads.models import *


def signup(request):
    if request.method == "GET":
        selected_plan = 'f'
        try:
            get_plan = request.GET.get('plan','f')
            if get_plan == 'f':
                selected_plan = 'f'
            elif get_plan == 'p':
                selected_plan = 'p'
            elif get_plan == 'g':
                selected_plan = 'g'
            elif get_plan == 'u':
                selected_plan = 'u'

        except:
            pass

        return render(request,'users/signup.html',{'plan':selected_plan})


    if request.method == "POST":
        plan = 'f'
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        plan = request.POST.get('plan','f')

        

    
        try:
            tos = request.POST['tos']

        except:
            return HttpResponse("Please accept the terms and conditions")

        if password != confirm_password:
            return HttpResponse("<div class='alert alert-danger'>Password does not match</div>")

        if len(User.objects.filter(email=email)) > 0:
            return HttpResponse("<div class='alert alert-danger'>User with this email already exists</div>")

        else:
            new_user= User.objects.create_user(first_name=first_name,last_name=last_name,email=email,phone=phone,password=password)
            set_secret = User.objects.get(id=new_user.id)
            set_secret.secret_id = abs(hash(str(new_user.id)+str(new_user.email)))
            set_secret.save()

            user_credit.objects.create(user=new_user,credits_remaining=100)
            user_auth = auth.authenticate(email=email,password=password)
            auth.login(request,user_auth)

            try:
                campaigns.objects.create(name="default campaign",description="default campaign description",user=new_user,is_active=True)
            except:
                pass

            if plan == 'f':
                get_package = packages.objects.get(name='FREE')
                subscription_data.objects.create(user=new_user,package=get_package)
            
            elif plan == 'p':
                get_package = packages.objects.get(name='PLATINUM')
                #subscription_data.objects.create(user=new_user,package=get_package)
                return HttpResponse("platinum")

            elif plan == 'g':
                get_package = packages.objects.get(name='GOLD')
                #subscription_data.objects.create(user=new_user,package=get_package)
                return HttpResponse("gold")
            
            elif plan == 'u':
                get_package = packages.objects.get(name='UNLIMITED')
                #subscription_data.objects.create(user=new_user,package=get_package)
                return HttpResponse("unlimited")

            

            return HttpResponse("<div class='alert alert-success'>Account created successfully ! Please <a href='/users/login/'>Login Now</a></div>")



def login(request):
    if request.method == "GET":
        return render(request,'users/login.html')

    if request.method == "POST":
      
        email = request.POST.get('email')
        password = request.POST.get('password')
        user_auth = auth.authenticate(email=email,password=password)
        if user_auth is not None:
            auth.login(request,user_auth)
            get_sub = subscription_data.objects.get(user=request.user)
            if get_sub.package.name == 'FREE' and get_sub.expire_date < datetime.date.today():
                get_user_credit=user_credit.objects.get(user=request.user)
                get_sub.expire_date = datetime.date.today() + datetime.timedelta(days=30)
                get_sub.save()
                get_user_credit.credits_remaining = get_sub.package.credits
                get_user_credit.save()
            
            if get_sub.package.name == 'UNLIMITED' and (get_sub.expire_date + datetime.timedelta(days=5)) < datetime.date.today():
                get_user_credit=user_credit.objects.get(user=request.user)
                get_sub.expire_date = datetime.date.today() + datetime.timedelta(days=30)
                get_sub.package = packages.objects.get(name='FREE')
                get_sub.save()

                get_user_credit.credits_remaining = 200
                get_user_credit.save()

            res=HttpResponse("login_successful")
            res.set_cookie('plati_key', value=request.user.secret_id, max_age=999999999999999, expires=datetime.datetime.now()+timedelta(days=365), path='/', domain=None, secure=False, httponly=False, samesite=None)
            res.set_cookie('name', value=request.user.first_name, max_age=999999999999999, expires=datetime.datetime.now()+timedelta(days=365), path='/', domain=None, secure=False, httponly=False, samesite=None)
            return res
        else:
            return HttpResponse("<div class='alert alert-danger'>Invalid Credentials</div>")



def change_alert_status(request):
    sel_u=User.objects.get(id=request.user.id)
    sel_u.alert_status = False
    sel_u.save()

    return redirect('dashboard_home')

@login_required(login_url='/users/login/')
def profile(request):
    if request.method == "GET":

        return render(request,'users/profile.html')

    if request.method=="POST":
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone = request.POST.get('phone')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')


        
        if password1 != password2:
            messages.info(request,"Password does not match")
            return redirect('profile')

        else:
            
            request.user.first_name = first_name
            request.user.last_name = last_name
            request.user.phone = phone
            if (password1 == "" and password2 == "") or (password1 ==  None and password2 == None):
                pass
            else:
                request.user.set_password(password1)
            request.user.save()

            messages.info(request,"Profile updated successfully")

            return redirect('profile')


        

def logout(request):
    auth.logout(request)
    return redirect('home_page')


def appsumo_code(request):
    if request.method == "GET":
        return render(request,'users/appsumo_code.html')

    if request.method == "POST":
        email = request.POST.get('email')
        code = request.POST.get('code')

        if code == "":
            return redirect('appsumo_code')

        if email == "":
            return redirect('appsumo_code')

        user_coupon.objects.create(email=email,code=code)

        return render(request,'users/appsumo_code_redeemed.html')




def process_percentage(request):
    get_per = request.user.file_process_percentage
    return JsonResponse({"percentage":round(get_per,2)})