# Generated by Django 2.1.7 on 2019-12-12 06:26

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0011_auto_20191211_1451'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='uuid',
            field=models.UUIDField(default=uuid.UUID('df61dd29-fbaf-41a1-b908-530a897db2c6'), verbose_name='用户JWT密钥'),
        ),
    ]
