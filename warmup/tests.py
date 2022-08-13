from django.test import TestCase

from users.models import *

def usercheck():
    obj = User.objects.all()

    for x in obj:
        print(x.email,'\n')