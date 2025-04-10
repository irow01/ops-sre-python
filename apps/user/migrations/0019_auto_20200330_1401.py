# Generated by Django 2.1.7 on 2020-03-30 06:01

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0018_auto_20200326_1427'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='uuid',
            field=models.UUIDField(default=uuid.UUID('1935b14f-5f1e-448b-9cc0-584633acd6cc'), verbose_name='用户JWT密钥'),
        ),
    ]
