# Generated by Django 2.1.7 on 2022-07-01 05:44

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0048_auto_20201203_1621'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='uuid',
            field=models.UUIDField(default=uuid.UUID('cb0f3b4a-4400-41a9-a2d9-c9ba18270751'), verbose_name='用户JWT密钥'),
        ),
    ]
