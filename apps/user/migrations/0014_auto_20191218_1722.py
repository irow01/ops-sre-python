# Generated by Django 2.1.7 on 2019-12-18 09:22

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0013_auto_20191213_1353'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='uuid',
            field=models.UUIDField(default=uuid.UUID('8d699c12-7bcd-4fa6-9f82-5a54aaea99de'), verbose_name='用户JWT密钥'),
        ),
    ]
