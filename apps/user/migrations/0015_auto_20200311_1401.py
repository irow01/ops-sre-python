# Generated by Django 2.1.7 on 2020-03-11 06:01

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0014_auto_20191218_1722'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='uuid',
            field=models.UUIDField(default=uuid.UUID('32827c5f-61d5-429b-b47c-2dd9618d2e8c'), verbose_name='用户JWT密钥'),
        ),
    ]
