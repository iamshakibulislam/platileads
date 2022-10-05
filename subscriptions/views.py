from locale import currency
import re
from webbrowser import get
from django.http import JsonResponse,HttpResponse
from django.shortcuts import render,redirect
import stripe
from datetime import datetime,timedelta
import json
import datetime
#import django csrf_exempt
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.conf import settings
from users.models import User, user_credit
from .models import *

#import django message
from django.contrib import messages

#import http404 exception
from django.http import Http404


stripe.api_key = settings.STRIPE_SECRET_KEY


@login_required(login_url='/users/login/')
def subscribe(request):
    if request.method == "GET":
        plan = ''
        price = 0
        get_plan = request.GET.get('plan')

        if get_plan == 'p':
            plan = 'platinum'
            price = 14

        elif get_plan == 'g':
            plan = 'gold'
            price = 39

        elif get_plan == 'u':

            plan = 'unlimited'
            price = 99

        elif get_plan == 'l':
            plan = "lifetime"
            price = 49
        return render(request,'subscriptions/subscription.html',{'plan':plan,'price':price,'plan_key':get_plan,'stripe_public_key':settings.STRIPE_PUBLIC_KEY})




@csrf_exempt
def create_payment_intent(request):
    get_plan = json.load(request)['items'][0]['plan']

    #print('selected plan is ',get_plan)

    price = 0

    if get_plan == 'p':
        price = 1400

    elif get_plan == 'g':
        price = 3900

    elif get_plan == 'u':
        price = 9900

    elif get_plan == 'l':
        price = 4900

    customer = None
    if request.user.customer_id == None or request.user.customer_id == '':
        customer = stripe.Customer.create(
            email=request.user.email,
            name=request.user.first_name+' '+request.user.last_name,
            
        )

        request.user.customer_id = customer.id
        request.user.save()

        customer = customer.id


    else:
        customer = request.user.customer_id

    
    if get_plan == 'p':
        #platinum plan 14 bucks for 30 days
        subscription = stripe.Subscription.create(
            customer=customer,
            items=[{
                'price': settings.STRIPE_PLATINUM_PLAN,
            }],
            payment_behavior='default_incomplete',
            expand=['latest_invoice.payment_intent'],
        )


        subscriptionId=subscription.id
        clientSecret=subscription.latest_invoice.payment_intent.client_secret

        

        return JsonResponse({'subscriptionId':subscriptionId,'clientSecret':clientSecret})

    


    
    if get_plan == 'g':
        #gold plan 39 bucks for 30 days
        subscription = stripe.Subscription.create(
            customer=customer,
            items=[{
                'price': settings.STRIPE_GOLD_PLAN,
            }],
            payment_behavior='default_incomplete',
            expand=['latest_invoice.payment_intent'],
        )


        subscriptionId=subscription.id
        clientSecret=subscription.latest_invoice.payment_intent.client_secret

        

        return JsonResponse({'subscriptionId':subscriptionId,'clientSecret':clientSecret})


    
    if get_plan == 'u':
        #unlimited plan 99 bucks for 30 days
        subscription = stripe.Subscription.create(
            customer=customer,
            items=[{
                'price': settings.STRIPE_UNLIMITED_PLAN,
            }],
            payment_behavior='default_incomplete',
            expand=['latest_invoice.payment_intent'],
        )


        subscriptionId=subscription.id
        clientSecret=subscription.latest_invoice.payment_intent.client_secret

        
       

        return JsonResponse({'subscriptionId':subscriptionId,'clientSecret':clientSecret})

    if get_plan == 'l':
        #life plan 99 bucks for 30 days
        subscription = stripe.PaymentIntent.create(
            customer=customer,
            amount = 4900,
            currency = "usd",
            
            payment_method_types=["card"],
            metadata={'is_one_time':True},
            #payment_behavior='default_incomplete',
            #expand=['latest_invoice.payment_intent'],
        )

        #print(subscription)
        subscriptionId=subscription.id
        clientSecret=subscription.client_secret

        
       

        return JsonResponse({'subscriptionId':subscriptionId,'clientSecret':clientSecret})




def thank_you(request):
    if request.GET.get('payment_intent')==None or request.GET.get('payment_intent') == "":
        raise Http404

    if request.GET.get('payment_intent_client_secret') == None or request.GET.get('payment_intent_client_secret') == "":
        raise Http404

    return render(request,'subscriptions/thank_you.html')




@csrf_exempt
def webhook(request):
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
    event = None
    payload = request.body
    sig_header = request.headers['STRIPE_SIGNATURE']

    try:
        event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )
    except ValueError as e:
            # Invalid payload
            raise e
    except stripe.error.SignatureVerificationError as e:
            # Invalid signature
        raise e

    

    try:
    

        customer_email=event['data']['object']['customer_email']
        
        invoice_pdf = event['data']['object']['invoice_pdf']
        
        amount_paid = event['data']['object']['amount_paid']
        

    
        
        plan_amount = event['data']['object']['lines']['data'][0]['plan']['amount']
        

        subscription_id = event['data']['object']['lines']['data'][0]['subscription']

        plan_id = event['data']['object']['lines']['data'][0]['plan']['id']
        



        
        
        
        
        if amount_paid == plan_amount and plan_id == settings.STRIPE_PLATINUM_PLAN:
            sel_user = User.objects.get(email=customer_email)
            #check if the user is already subscribed or not
            if sel_user.subscription_id == None or sel_user.subscription_id == '':
                sel_user.subscription_id = subscription_id
            else:
                del_sub=stripe.Subscription.delete(sel_user.subscription_id)
                if del_sub.status == 'canceled':
                    sel_user.subscription_id = subscription_id

            sel_user.save()
            sel_package = packages.objects.get(name='PLATINUM')

            try:
                get_user_sub=subscription_data.objects.get(user=sel_user)
                get_user_sub.package = sel_package
                get_user_sub.expire_date = datetime.now() + timedelta(days=30)
                get_user_sub.save()

            except:
                new_sub = subscription_data(user=sel_user,package=sel_package)
                new_sub.save()

            try:
                sel_credit=user_credit.objects.get(user=sel_user)
                sel_credit.credits_remaining = sel_package.credits
                sel_credit.save()

            except:
                new_credit = user_credit(user=sel_user,credits_remaining=sel_package.credits)
                new_credit.save()

            
            try:
                sel_ref = sel_user.referred_by
                pay_aff = User.objects.get(id=sel_ref.id)
                pay_aff.balance += 5.6
                pay_aff.save()

                try:
                    f_ref = pay_aff.referred_by
                    f_u = User.objects.get(id=f_ref.id)
                    f_u.balance += 1.12
                    f_u.save()

                except:
                    pass
            except:
                pass


            


        
        if amount_paid == plan_amount and plan_id == settings.STRIPE_GOLD_PLAN:
            sel_user = User.objects.get(email=customer_email)
            if sel_user.subscription_id == None or sel_user.subscription_id == '':
                sel_user.subscription_id = subscription_id
            else:
                del_sub=stripe.Subscription.delete(sel_user.subscription_id)
                
                if del_sub.status == 'canceled':
                    sel_user.subscription_id = subscription_id
            
            sel_user.save()
            sel_package = packages.objects.get(name='GOLD')

            try:
                get_user_sub=subscription_data.objects.get(user=sel_user)
                get_user_sub.package = sel_package
                get_user_sub.expire_date = datetime.now() + timedelta(days=30)
                get_user_sub.save()

            except:
                new_sub = subscription_data(user=sel_user,package=sel_package)
                new_sub.save()

            try:
                sel_credit=user_credit.objects.get(user=sel_user)
                sel_credit.credits_remaining = sel_package.credits
                sel_credit.save()

            except:
                new_credit = user_credit(user=sel_user,credits_remaining=sel_package.credits)
                new_credit.save()


            try:
                sel_ref = sel_user.referred_by
                pay_aff = User.objects.get(id=sel_ref.id)
                pay_aff.balance += 15.6
                pay_aff.save()

                try:
                    f_ref = pay_aff.referred_by
                    f_u = User.objects.get(id=f_ref.id)
                    f_u.balance += 3.12
                    f_u.save()

                except:
                    pass
            except:
                pass

            

            
        
        if amount_paid == plan_amount and plan_id == settings.STRIPE_UNLIMITED_PLAN:
            sel_user = User.objects.get(email=customer_email)
            if sel_user.subscription_id == None or sel_user.subscription_id == '':
                sel_user.subscription_id = subscription_id
            else:
                del_sub=stripe.Subscription.delete(sel_user.subscription_id)
                if del_sub.status == 'canceled':
                    sel_user.subscription_id = subscription_id
            
            sel_user.save()
            sel_package = packages.objects.get(name='UNLIMITED')

            try:
                get_user_sub=subscription_data.objects.get(user=sel_user)
                get_user_sub.package = sel_package
                get_user_sub.expire_date = datetime.now() + timedelta(days=30)
                get_user_sub.save()

            except:
                new_sub = subscription_data(user=sel_user,package=sel_package)
                new_sub.save()

            try:
                sel_credit=user_credit.objects.get(user=sel_user)
                sel_credit.credits_remaining = sel_package.credits
                sel_credit.save()

            except:
                new_credit = user_credit(user=sel_user,credits_remaining=sel_package.credits)
                new_credit.save()

            
            try:
                sel_ref = sel_user.referred_by
                pay_aff = User.objects.get(id=sel_ref.id)
                pay_aff.balance += 39.6
                pay_aff.save()

                try:
                    f_ref = pay_aff.referred_by
                    f_u = User.objects.get(id=f_ref.id)
                    f_u.balance += 7.92
                    f_u.save()

                except:
                    pass
            except:
                pass


    
    except:
        try:
            #print("event is ",event)
           # event = json.loads(event)
            customer_id = event["data"]["object"]["customer"]
            is_paid = event["data"]["object"]["charges"]["data"][0]["paid"]
            is_one_time = event["data"]["object"]["metadata"]["is_one_time"]

            if (is_paid == True or is_paid == "True") and (is_one_time==True or is_one_time == "True"):
                sel_user = User.objects.get(customer_id=customer_id)
                sel_package=packages.objects.get(name="LIFETIME")
                try:
                    subdata=subscription_data.objects.get(user=sel_user)
                    subdata.package = sel_package
                    subdata.save()
                except:
                    subscription_data.objects.create(user=sel_user,package = sel_package)

                update_credit = user_credit.objects.get(user=sel_user)
                update_credit.credits_remaining = sel_package.credits
                update_credit.save()

                get_referer = sel_user.referred_by

                if get_referer != None and get_referer != "" and get_referer != " " and get_referer != 0:
                    sel_ref = User.objects.get(id=get_referer.id)

                    sel_ref.balance = sel_ref.balance + 19.6
                    sel_ref.save()







            print("customer id = ",customer_id," is_paid = ",is_paid," is_one_time ",is_one_time)

        except:
            pass


    




    return JsonResponse({'success':True})



@login_required(login_url='users/login/')
def subscriptions(request):
    if request.method == "GET":
        current_subscription = subscription_data.objects.get(user=request.user)
        credit = user_credit.objects.get(user=request.user)
        

        return render(request,'subscriptions/user_subscriptions.html',{'sub_info':current_subscription,'credit':credit})


@login_required(login_url='users/login/')
def cancel_subscription(request):
    if request.method == "GET":
        current_subscription = subscription_data.objects.get(user=request.user)
        current_subscription.package = packages.objects.get(name='FREE')
        current_subscription.save()
        cancel_sub = stripe.Subscription.delete(request.user.subscription_id)
        if cancel_sub.status == 'canceled':
            messages.info(request,'subscription has been cancelled !')
            request.user.subscription_id = ''
            request.user.save()
            return redirect('subscriptions')

        else:
            messages.info(request,'subscription could not be cancelled !')
            return redirect('subscriptions')
