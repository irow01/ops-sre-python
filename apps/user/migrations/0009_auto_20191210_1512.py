# Generated by Django 2.1.7 on 2019-12-10 07:12

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0008_auto_20191210_1437'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='uuid',
            field=models.UUIDField(default=uuid.UUID('0e9f407b-7959-43cc-aa9a-f134403ba409'), verbose_name='用户JWT密钥'),
        ),
    ]
