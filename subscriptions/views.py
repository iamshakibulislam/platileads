from django.http import JsonResponse
from django.shortcuts import render
import stripe
import json
#import django csrf_exempt
from django.views.decorators.csrf import csrf_exempt


stripe.api_key = "sk_test_51K4KJjHrW1RE7YcK2tbMoVqvzgspfjw6iNosIw11bZ0dYg4pBOyY1yjIVZBwW9NMvw5BzNMjnGrR84naYV2M2Vmy00bRq55qAs"

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

            plan = 'ultimate'
            price = 99
        return render(request,'subscriptions/subscription.html',{'plan':plan,'price':price,'plan_key':get_plan})




@csrf_exempt
def create_payment_intent(request):
    get_plan = json.load(request)['items'][0]['plan']

    print('selected plan is ',get_plan)

    price = 0

    if get_plan == 'p':
        price = 1400

    elif get_plan == 'g':
        price = 3900

    elif get_plan == 'u':
        price = 9900

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
                'price': 'price_1KezL2HrW1RE7YcKBsLm3YPy',
            }],
            payment_behavior='default_incomplete',
            expand=['latest_invoice.payment_intent'],
        )


        subscriptionId=subscription.id
        clientSecret=subscription.latest_invoice.payment_intent.client_secret

        request.user.subscription_id = subscriptionId
        request.user.save()

        return JsonResponse({'subscriptionId':subscriptionId,'clientSecret':clientSecret})

    


    
    if get_plan == 'g':
        #gold plan 39 bucks for 30 days
        subscription = stripe.Subscription.create(
            customer=customer,
            items=[{
                'price': 'price_1Kf0kkHrW1RE7YcKLkpGXhdd',
            }],
            payment_behavior='default_incomplete',
            expand=['latest_invoice.payment_intent'],
        )


        subscriptionId=subscription.id
        clientSecret=subscription.latest_invoice.payment_intent.client_secret

        request.user.subscription_id = subscriptionId
        request.user.save()

        return JsonResponse({'subscriptionId':subscriptionId,'clientSecret':clientSecret})


    
    if get_plan == 'u':
        #unlimited plan 99 bucks for 30 days
        subscription = stripe.Subscription.create(
            customer=customer,
            items=[{
                'price': 'price_1Kf0m0HrW1RE7YcKcXXu11gz',
            }],
            payment_behavior='default_incomplete',
            expand=['latest_invoice.payment_intent'],
        )


        subscriptionId=subscription.id
        clientSecret=subscription.latest_invoice.payment_intent.client_secret

        request.user.subscription_id = subscriptionId
        request.user.save()

        return JsonResponse({'subscriptionId':subscriptionId,'clientSecret':clientSecret})

