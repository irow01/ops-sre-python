# Generated by Django 2.1.7 on 2020-06-17 08:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('deploy', '0020_auto_20200612_1619'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='subproject',
            name='job_name',
        ),
    ]
