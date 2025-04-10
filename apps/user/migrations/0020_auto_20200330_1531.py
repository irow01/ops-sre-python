# Generated by Django 2.1.7 on 2020-03-30 07:31

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0019_auto_20200330_1401'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='uuid',
            field=models.UUIDField(default=uuid.UUID('d3ae9a22-e209-4b32-9e28-20182fce866d'), verbose_name='用户JWT密钥'),
        ),
    ]
