# Generated by Django 2.1.7 on 2023-03-21 09:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('localDeploy', '0003_localorder_patch'),
    ]

    operations = [
        migrations.AlterField(
            model_name='localorder',
            name='patch',
            field=models.CharField(default='NULL', max_length=20, verbose_name='概要'),
        ),
    ]
