# Generated by Django 4.0.3 on 2022-03-19 11:44

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subscriptions', '0004_alter_subscription_data_expire_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscription_data',
            name='expire_date',
            field=models.DateField(blank=True, default=datetime.datetime(2022, 4, 18, 17, 44, 0, 913037), null=True),
        ),
    ]
