# Generated by Django 2.1.7 on 2019-11-29 08:59

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='uuid',
            field=models.UUIDField(default=uuid.UUID('75ac8eb7-2691-478a-abe7-899af6e76433'), verbose_name='用户JWT密钥'),
        ),
    ]
