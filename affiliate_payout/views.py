from django.shortcuts import redirect, render
from .models import *
#import django messages
from django.contrib import messages

def add_bank_account(request):
    if request.method == "GET":
        get_obj = None
        try:
            get_obj = bank_account_details.objects.get(user=request.user)
        except:
            pass
        return render(request,'dashboard/add_bank_account.html',{'data':get_obj})

    
    if request.method == "POST":
        post_obj = bank_account_details.objects.filter(user=request.user)
        if post_obj.exists():
            post_obj.update(account_number=request.POST.get('bank_account_number'),bank_name=request.POST.get('bank_name'),branch_name=request.POST.get('bank_branch_name'),routing_number=request.POST.get('bank_routing_number'),account_type=request.POST.get('account_type'))
            messages.success(request,'Bank Account  Updated Successfully')
        else:
            messages.success(request,'Bank account  added successfully')
            bank_account_details.objects.create(account_number=request.POST.get('bank_account_number'),bank_name=request.POST.get('bank_name'),branch_name=request.POST.get('bank_branch_name'),routing_number=request.POST.get('bank_routing_number'),account_type=request.POST.get('account_type'),user=request.user)
        return redirect('add_bank_account')





def request_payout(request):
    if request.method == "GET":
        return render(request,'dashboard/request_payout.html')

    if request.method == "POST":
        amount = request.POST.get('amount',None)

        if float(amount) < 25 :
            messages.success(request,'Minimum payout amount is $25')
            return redirect('request_payout')

        if amount != None and request.user.balance >= float(amount):
            sel_bank = bank_account_details.objects.get(user=request.user)
            payout_requests.objects.create(amount=amount,payment_method=sel_bank,user=request.user)

            bal = request.user.balance
            bal = bal - float(amount)
            request.user.balance = bal
            request.user.save()

            messages.success(request,'Payout request sent successfully')

            return redirect('request_payout')

        else:
            messages.success(request,'Insufficient balance')
            return redirect('request_payout')
        

        messages.info(request,'Something went wrong ! please try again later')

        return redirect('request_payout')