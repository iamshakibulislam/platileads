from django.shortcuts import render,redirect
from django.http import HttpResponse
from users.models import User
from time import sleep
from django.contrib import auth


def signup(request):
    if request.method == "GET":
        return render(request,'users/signup.html')


    if request.method == "POST":
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        sleep(5)
        try:
            tos = request.POST['tos']

        except:
            return HttpResponse("Please accept the terms and conditions")

        if password != confirm_password:
            return HttpResponse("<div class='alert alert-danger'>Password does not match</div>")

        if len(User.objects.filter(email=email)) > 0:
            return HttpResponse("<div class='alert alert-danger'>User with this email already exists</div>")

        else:
            User.objects.create_user(first_name=first_name,last_name=last_name,email=email,phone=phone,password=password)
            return HttpResponse("<div class='alert alert-success'>Account created successfully ! Please Login</div>")



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