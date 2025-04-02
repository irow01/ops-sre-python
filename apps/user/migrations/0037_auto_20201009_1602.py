# Generated by Django 2.1.7 on 2020-10-09 08:02

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0036_auto_20201009_1600'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='uuid',
            field=models.UUIDField(default=uuid.UUID('4522155e-c351-4b9f-bfcd-308435ddf9c0'), verbose_name='用户JWT密钥'),
        ),
    ]
