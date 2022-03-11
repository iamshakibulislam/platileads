from django.db import models
from users.models import User


class packages(models.Model):
    name = models.CharField(max_length=100)
    credits = models.IntegerField(default=0)
    price_per_month = models.IntegerField(default=0)
    price_per_year = models.IntegerField(default=0)

    def __str__(self):
        return str(self.name)+'  '+str(self.credits)
    
    class Meta:
        verbose_name = 'Package'
        verbose_name_plural = 'Packages'


class subscription_data(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    package = models.ForeignKey(packages,on_delete=models.CASCADE)
    start_date = models.DateField(auto_now_add=True)
    expire_date = models.DateField(null=True,blank=True,auto_now=False,auto_now_add=False)
    is_active = models.BooleanField(default=True)
    last_update = models.DateField(auto_now=True)


    def __str__(self):
        return str(self.user.email)+'  '+str(self.package.name)

    class Meta:
        verbose_name = 'Subscription'
        verbose_name_plural = 'Subscriptions'