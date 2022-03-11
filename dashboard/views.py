#from http.client import HTTPResponse
from django.shortcuts import render
from django.http import HttpResponse
from time import sleep
from xls2xlsx import XLS2XLSX
import os
import csv
from .custom_scripts import get_mx_records,is_valid_email,xlsx_info,xlsx_write_on_new_column,xlsx_retrive_column_data,csv_to_xlsx
from .models import *

def dashboard_home(request):
    return render(request,'dashboard/index.html')

def email_verification(request):
    if request.method == "GET":
        return render(request,'dashboard/single_email_verification.html')

    if request.method == "POST":
        email = request.POST.get('email')

        if email == None or email == "":
            return HttpResponse("invalid_email")

        is_exists = False

        

        #checking the email validity
        get_mx = get_mx_records(email)[-1]

        is_exists = is_valid_email(get_mx,email)

        #end of checking email validity
        
        if is_exists == False:
           
            return HttpResponse("invalid_email")

        elif is_exists == True:
            
            return HttpResponse("valid_email")

        else:
             return HttpResponse("something_went_wrong")


def bulk_email_verification(request):
    if request.method == "GET":
        return render(request,'dashboard/bulk_email_verification.html')

    if request.method == "POST":
        try:
            get_this_user_files = file_uploader.objects.filter(user=request.user)
            for file in get_this_user_files:
                try:
                    os.remove(file.file.path)
                except:
                    pass
                try:
                    os.remove(file.file.path[:-3]+"xlsx")
                except:
                    pass
                file.delete()
        except:
            pass
        get_file = request.FILES.get('file')

        file_instance = file_uploader(user=request.user,file=get_file)


        file_instance.save()

        file_path = file_instance.file.path
        
        #check file extension
        file_extension = file_path.split('.')[-1]


        if file_extension == "xls":
            new_file_path = file_path[:-3]+"xlsx"
            thexls = XLS2XLSX(file_path)
            thexls.to_xlsx(new_file_path)

            information = xlsx_info(new_file_path)


        
        

        elif file_extension == "csv":

            #convert csv to xlsx
            
            check= csv_to_xlsx(file_path,file_instance.file.name)
            new_path = file_instance.file.path[:len(file_instance.file.path)-3]+"xlsx"
            information = xlsx_info(new_path)
           
           # file_instance.file.path=file_instance.file.path[:len(file_instance.file.path)-3]+"xlsx"
            

        elif file_extension == "xlsx":

        
            information = xlsx_info(file_path)

        else:
            os.remove(file_instance.file.path)
            return HttpResponse("invalid_file_extension")

        all_columns = information['column_names']



        return render(request,'dashboard/components/column_selection.html',{'all_columns':all_columns})

           
        

