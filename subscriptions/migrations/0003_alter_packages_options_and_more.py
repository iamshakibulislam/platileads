# Generated by Django 4.0.3 on 2022-03-09 05:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('subscriptions', '0002_alter_subscription_data_user'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='packages',
            options={'verbose_name': 'Package', 'verbose_name_plural': 'Packages'},
        ),
        migrations.AlterModelOptions(
            name='subscription_data',
            options={'verbose_name': 'Subscription', 'verbose_name_plural': 'Subscriptions'},
        ),
    ]
