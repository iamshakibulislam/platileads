# Generated by Django 4.0.3 on 2022-03-28 05:42

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('leads', '0007_leads_employee_total_leads_industry_leads_location'),
    ]

    operations = [
        migrations.AlterField(
            model_name='campaigns',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
