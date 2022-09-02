"""
Django settings for lead_generation_software project.

Generated by 'django-admin startproject' using Django 4.0.3.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""

from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-8^*no3qd*^_&oslckj)yqgutk^rri!klzj1k))#(b%hcl=szql'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_crontab',
    'users',
    'dashboard',
    'leads',
    'subscriptions',
    'company_email_finder',
    'affiliate_payout',
    'warmup',
    'email_sending',
    'ckeditor',
    'widget_tweaks',

]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'lead_generation_software.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'lead_generation_software.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases



# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'users.User'


MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR,'media')

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR,'static')
STATICFILES_DIRS = [os.path.join(BASE_DIR,'staticfiles')]

#stripe secret keys FOR TEST
'''
STRIPE_SECRET_KEY = "sk_test_51K4KJjHrW1RE7YcK2tbMoVqvzgspfjw6iNosIw11bZ0dYg4pBOyY1yjIVZBwW9NMvw5BzNMjnGrR84naYV2M2Vmy00bRq55qAs"
STRIPE_PUBLIC_KEY = "pk_test_51K4KJjHrW1RE7YcKA4VfBlE9J56SK1fmfMlGMjlZof0G7LRJJeeoPrnkSon2aFVzqbaeom0IjorWDKc5c0yZWGSb009JEbw4o2"
'''

#STRIPE SECRET KEYS FOR LIVE


STRIPE_SECRET_KEY = "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"
STRIPE_PUBLIC_KEY = "pk_live_51K4KJjHrW1RE7YcKGX1lm6vR4aJIHdp5em0gLoP7zV7cbwDbjmrJNU26kBmRxu6g3UViY3UGXneaqvymJp2r7r9M00Xm8MWcvx"

#stripe real LIVE recurring package price

STRIPE_PLATINUM_PLAN = "price_1Kjib5HrW1RE7YcK9nBAxzMl"
STRIPE_GOLD_PLAN = "price_1KjickHrW1RE7YcKOD7NflVk"
STRIPE_UNLIMITED_PLAN = "price_1KjidzHrW1RE7YcKckW1q7A9"



#stripe test recurring packages price COMMENT OUT FOR PRODUCTION
'''
STRIPE_PLATINUM_PLAN = "price_1KezL2HrW1RE7YcKBsLm3YPy"
STRIPE_GOLD_PLAN = "price_1Kf0kkHrW1RE7YcKLkpGXhdd"
STRIPE_UNLIMITED_PLAN = "price_1Kf0m0HrW1RE7YcKcXXu11gz"
'''


#STRIPE TEST WEBHOOK SECRET KEY
'''
STRIPE_WEBHOOK_SECRET = "whsec_L1Q3R64nDPK40SnAME2ylRzfzfeW5GwM"
'''


#STRIPE LIVE WEBHOOK SECRET

STRIPE_WEBHOOK_SECRET = "whsec_3pyNfTdYgX2N1fE0yMvJFpnNthPIpiWb"


#scraperapi APIKEY
SCRAPER_API_KEY = "PFG7DzbFAA8dpiMT28HGSA"

#openAI APIKEY
OPENAI_API_KEY = "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"

#django email settings

EMAIL_MAIL_HTML = 'users/password-reset-email-template.html'
DEFAULT_FROM_EMAIL = 'platileads <support@platileads.com>'
EMAIL_BACKEND ='django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.zoho.com'
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST_USER = 'support@platileads.com'
EMAIL_HOST_PASSWORD = 'pURgSSJVVLny'



#local testing database

if DEBUG == True:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }



#production database aws ses service
'''
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'platileads',
        'USER': 'shakil',
        'PASSWORD': 'Platileads121',
        'HOST': 'platileads.c3mwtiaam63p.us-east-1.rds.amazonaws.com',
        'PORT': '3306',
        
        
        }
       
}
'''


#local production database
if DEBUG == False:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'platileads',
            'USER': 'shakil',
            'PASSWORD': 'Shakil121@',
            'HOST': 'localhost',
            'PORT': '3306',
            
            
            }
        
    }


CRONJOBS = [
    ('59 16 * * *', 'warmup.cronjob.warmup_emails'),
    ('0 */6 * * *', 'email_sending.cron.check_reply'),
    ('0 0 * * *', 'email_sending.cron.send_email_campaign')
]




CKEDITOR_BASEPATH = "/static/ckeditor/ckeditor/"

CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'Full',
        'height': 250,
        'width': 850,
        'editorplaceholder':'Message starts from here'
    },

    'followup': {
        'toolbar': 'Full',
        'height':100,
        'editorplaceholder':"Followup message here"
    }

}