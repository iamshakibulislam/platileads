from django.shortcuts import render
from .models import *
from django.http import HttpResponse
def create_campaign(request):
    if request.method == "POST":
        name = request.POST.get('name')
        description = request.POST.get('description')
        get_all_camp = campaigns.objects.filter(user=request.user)
        is_active =  False

        if len(get_all_camp) == 0:
            is_active = True
        campaigns.objects.create(user=request.user,name=name,description=description,is_active=is_active)
        return HttpResponse("<div class='alert alert-success' style='width:36rem'>Campaign created successfully</div>")




    
