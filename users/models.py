from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager




class UserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """
    def create_user(self, email, password, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        if not email:
            raise ValueError(_('The Email must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(email, password, **extra_fields)




class User(AbstractUser):
    join_date = models.DateTimeField(auto_now_add=True)
    email = models.EmailField(max_length=60, unique=True)
    username = None
    first_name = models.CharField(max_length=50,null=False,blank=False)
    last_name = models.CharField(max_length=50,null=True,blank=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    phone = models.CharField(max_length=20,null=True,blank=True)
    alert_status = models.BooleanField(default=True)
    customer_id = models.CharField(max_length=100,null=True,blank=True)
    subscription_id = models.CharField(max_length=100,null=True,blank=True)
    secret_id = models.CharField(max_length=100,null=True,blank=True)

    referred_by = models.ForeignKey('self',null=True,blank=True,on_delete=models.SET_NULL)
    is_affiliate = models.BooleanField(default=False)
    balance = models.FloatField(default=0)
    #track user uploaded file progress while processing either for bulk email verification or finding . It will update the status and store 
    #the % of progress of the file . Later this field will be called from frontend to show the progress of the file
    file_process_percentage = models.FloatField(default=0)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name','last_name']


    objects = UserManager()

    def __str__(self):
        return str(self.email)+' | name : '+str(self.first_name)

    class Meta:
        
        verbose_name = 'User'
        verbose_name_plural = 'Users'




class user_credit(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    credits_remaining = models.IntegerField(default=0)


    def __str__(self):
        return str(self.user.first_name)+' | credits : '+str(self.credits_remaining)

    class Meta:
        verbose_name = 'User Credit'
        verbose_name_plural = 'User Credits'


class coupon_codes(models.Model):
    code = models.CharField(max_length=50,null=False,blank=False)
    discount = models.IntegerField(default=0)
    bonus_credit = models.IntegerField(default=0)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return str(self.code)

    class Meta:
        verbose_name = 'Coupon Code'
        verbose_name_plural = 'Coupon Codes'


class user_coupon(models.Model):
    email = models.CharField(max_length=100,null=False,blank=False)
    code = models.CharField(max_length=50,null=False,blank=False)
    has_redeemed = models.BooleanField(default=False)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return str(self.email)+' | '+str(self.code) + ' | '+str(self.has_redeemed)


