from django.shortcuts import render,redirect
from django.http import HttpResponse
from users.models import *
from time import sleep
from django.contrib import auth
from subscriptions.models import packages,subscription_data


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
            user_credit.objects.create(user=new_user,credits_remaining=200)
            user_auth = auth.authenticate(email=email,password=password)
            auth.login(request,user_auth)

            if plan == 'f':
                get_package = packages.objects.get(name='FREE')
                subscription_data.objects.create(user=new_user,package=get_package)
            '''
            elif plan == 'p':
                get_package = packages.objects.get(name='PLATINUM')
                subscription_data.objects.create(user=new_user,package=get_package)

            elif plan == 'g':
                get_package = packages.objects.get(name='GOLD')
                subscription_data.objects.create(user=new_user,package=get_package)
            
            elif plan == 'u':
                get_package = packages.objects.get(name='UNLIMITED')
                subscription_data.objects.create(user=new_user,package=get_package)

            '''

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
            return HttpResponse("login_successful")
        else:
            return HttpResponse("<div class='alert alert-danger'>Invalid Credentials</div>")



def change_alert_status(request):
    sel_u=User.objects.get(id=request.user.id)
    sel_u.alert_status = False
    sel_u.save()

    return redirect('dashboard_home')
