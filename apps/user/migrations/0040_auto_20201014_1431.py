# Generated by Django 2.1.7 on 2020-10-14 06:31

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0039_auto_20201013_1535'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='uuid',
            field=models.UUIDField(default=uuid.UUID('00fa6615-7657-4356-b0be-f3905ff6cfb3'), verbose_name='用户JWT密钥'),
        ),
    ]
