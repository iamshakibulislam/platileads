from django.db import models
from users.models import User

class warmup_campaign(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    email = models.EmailField(max_length=100)
    app_password = models.CharField(max_length=100)
    start_count = models.IntegerField(default=1)
    increament_count = models.IntegerField(default=2)
    end_at = models.DateField(null=False,blank=False)
    provider = models.CharField(max_length=100,default='gmail')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)


    def __str__(self):
        return str(self.email)


class warmup_track(models.Model):
    campaign = models.ForeignKey(warmup_campaign,on_delete=models.CASCADE)
    total_sent = models.IntegerField(default=0)
    today_sent = models.IntegerField(default=0)
    spam_count = models.IntegerField(default=0)
    moved_to_inbox = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return str(self.campaign)








