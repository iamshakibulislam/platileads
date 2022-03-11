from django.db import models
from users.models import User

class leads(models.Model):
    date = models.DateField(auto_now_add=True)
    first_name = models.CharField(max_length=50,null=True,blank=True)
    last_name = models.CharField(max_length=50,null=True,blank=True)
    email = models.EmailField(max_length=60,null=True,blank=True)
    phone = models.CharField(max_length=20,null=True,blank=True)
    company = models.CharField(max_length=100,null=True,blank=True)
    website = models.CharField(max_length=100,null=True,blank=True)
    position = models.CharField(max_length=100,null=True,blank=True)
    linkedin_profile = models.URLField(max_length=400,null=True,blank=True)

    def __str__(self):
        return str(self.first_name)+' '+str(self.email)

    

    class Meta:
        verbose_name = 'Lead'
        verbose_name_plural = 'Leads'

class campaigns(models.Model):
    name = models.CharField(max_length=100)
    date = models.DateField(auto_now_add=True)
    user = models.ForeignKey(User,on_delete=models.SET_NULL,null=True)
    is_active = models.BooleanField(default=True)
    updated_at = models.DateField(auto_now=True)

    def __str__(self):
        return str(self.name)+' | created by: '+str(self.user.first_name)+' '+str(self.user.email)
    
    class Meta:
        verbose_name = 'Campaign'
        verbose_name_plural = 'Campaigns'



class campaign_leads(models.Model):
    date = models.DateField(auto_now_add=True)
    campaign = models.ForeignKey(campaigns,on_delete=models.CASCADE)
    lead = models.ForeignKey(leads,on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    updated_at = models.DateField(auto_now=True)

    def __str__(self):
        return str(self.campaign.name)+' | '+str(self.lead.first_name)+' '+str(self.lead.email)

    class Meta:
        verbose_name = 'Campaign Lead'
        verbose_name_plural = 'Campaign Leads'

