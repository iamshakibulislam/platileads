from django.shortcuts import render


def home_page(request):
    if request.method == "GET":
        return render(request,'home/index.html')