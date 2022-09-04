from django.db import models
from users.models import User
from ckeditor.fields import RichTextField

class emails_for_campaign(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    email = models.EmailField(max_length=255)
    app_password = models.CharField(max_length=255)
    provider = models.CharField(max_length=255,default='gmail')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.email



class contact_campaign(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.name

class sending_campaigns(models.Model):
    campaign_name = models.CharField(max_length=255)
    email = models.ForeignKey(emails_for_campaign, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_expired = models.BooleanField(default=False)
    followup_sequence = models.IntegerField(default=0)
    contact_book = models.ForeignKey(contact_campaign,on_delete=models.CASCADE,null=True)


    def __str__(self):
        return self.campaign_name

    class Meta:
        verbose_name_plural = 'sending campaigns'
        verbose_name = 'sending campaign'


class email_messages(models.Model):
    campaign = models.ForeignKey(sending_campaigns, on_delete=models.CASCADE)
    subject = models.CharField(max_length=255)
    message = RichTextField(null=True)
    delivery_date = models.DateTimeField(null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_sent = models.BooleanField(default=False)

    def __str__(self):
        return self.subject

    class Meta:
        verbose_name_plural = 'email messages'
        verbose_name = 'email message'





class contact_list(models.Model):
    contact_campaign = models.ForeignKey(contact_campaign, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255,null=True,blank=True)
    last_name = models.CharField(max_length=255,null=True,blank=True)
    email = models.EmailField(max_length=255)
    company = models.CharField(max_length=255,null=True,blank=True)
    phone = models.CharField(max_length=255,null=True,blank=True)
    position = models.CharField(max_length=255,null=True,blank=True)
    website = models.CharField(max_length=255,null=True,blank=True)
    country = models.CharField(max_length=255,null=True,blank=True)
    city = models.CharField(max_length=255,null=True,blank=True)
    state = models.CharField(max_length=255,null=True,blank=True)
    address = models.CharField(max_length=255,null=True,blank=True)
    other = models.CharField(max_length=255,null=True,blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.email

    class Meta:
        verbose_name_plural = 'contact list'
        verbose_name = 'contact list'

class sending_track(models.Model):
    campaign = models.ForeignKey(sending_campaigns,on_delete=models.CASCADE)
    sent_to = models.ForeignKey(contact_list,on_delete=models.CASCADE)
    is_replied = models.BooleanField(default=False)
    is_opened = models.BooleanField(default=False)

    def __str__(self):
        return str(self.sent_to)

class sending_campaign_track(models.Model):
    campaign = models.ForeignKey(sending_campaigns, on_delete=models.CASCADE)
    total_sent = models.IntegerField(default=0)
    opened_total = models.IntegerField(default=0)
    replied_total = models.IntegerField(default=0)
    followedup_total = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'sending campaigns track'
        verbose_name = 'sending campaign track'



class uploaded_files(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    file = models.FileField(upload_to='media/uploads')

    def __str__(self):
        return str(self.user.email)


