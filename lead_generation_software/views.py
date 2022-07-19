from django.shortcuts import render


def home_page(request):
    if request.method == "GET":
        return render(request,'home/index.html')


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