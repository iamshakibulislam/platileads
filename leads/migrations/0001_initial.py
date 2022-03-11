# Generated by Django 4.0.3 on 2022-03-09 05:31

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='leads',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(auto_now_add=True)),
                ('first_name', models.CharField(blank=True, max_length=50, null=True)),
                ('last_name', models.CharField(blank=True, max_length=50, null=True)),
                ('email', models.EmailField(blank=True, max_length=60, null=True)),
                ('phone', models.CharField(blank=True, max_length=20, null=True)),
                ('company', models.CharField(blank=True, max_length=100, null=True)),
                ('website', models.CharField(blank=True, max_length=100, null=True)),
                ('position', models.CharField(blank=True, max_length=100, null=True)),
                ('linkedin_profile', models.CharField(blank=True, max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='campaigns',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('date', models.DateField(auto_now_add=True)),
                ('is_active', models.BooleanField(default=True)),
                ('updated_at', models.DateField(auto_now=True)),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='campaign_leads',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(auto_now_add=True)),
                ('is_active', models.BooleanField(default=True)),
                ('updated_at', models.DateField(auto_now=True)),
                ('campaign', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='leads.campaigns')),
                ('lead', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='leads.leads')),
            ],
        ),
    ]
