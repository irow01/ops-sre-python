# Generated by Django 2.1.7 on 2020-10-09 07:56

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0034_auto_20200706_1728'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='uuid',
            field=models.UUIDField(default=uuid.UUID('a40a47d0-e977-4c40-9fd4-64ca1d98474d'), verbose_name='用户JWT密钥'),
        ),
    ]
