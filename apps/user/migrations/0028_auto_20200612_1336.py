# Generated by Django 2.1.7 on 2020-06-12 05:36

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0027_auto_20200610_1550'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='uuid',
            field=models.UUIDField(default=uuid.UUID('830b1d51-b94f-44db-a542-8a16c3475423'), verbose_name='用户JWT密钥'),
        ),
    ]
