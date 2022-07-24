from django.db import models
from users.models import *

class bank_account_details(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    account_number = models.CharField(max_length=100)
    bank_name = models.CharField(max_length=100)
    branch_name = models.CharField(max_length=100,blank=True,null=True)
    routing_number = models.CharField(max_length=100,blank=True,null=True)
    account_type = models.CharField(max_length=100,default="personal")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.user.first_name
    
    class Meta:
        verbose_name = 'Bank Account Detail'
        verbose_name_plural = 'Bank Account Details'



class payout_requests(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    amount = models.IntegerField(default=0)
    payment_method = models.ForeignKey(bank_account_details,on_delete=models.SET_NULL,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return str(self.user.first_name) + " | " + str(self.amount)

    class Meta:
        verbose_name = "payout request"
        verbose_name_plural ="payout requests"
