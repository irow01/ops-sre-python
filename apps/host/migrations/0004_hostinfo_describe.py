# Generated by Django 2.1.7 on 2020-10-15 08:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('host', '0003_auto_20201014_1431'),
    ]

    operations = [
        migrations.AddField(
            model_name='hostinfo',
            name='describe',
            field=models.CharField(default='', max_length=50, verbose_name='简述'),
        ),
    ]
