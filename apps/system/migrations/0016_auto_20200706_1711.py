# Generated by Django 2.1.7 on 2020-07-06 09:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0015_auto_20200706_1650'),
    ]

    operations = [
        migrations.AlterField(
            model_name='imageitems',
            name='image_select',
            field=models.ImageField(blank=True, null=True, upload_to=None, verbose_name='图片路径'),
        ),
    ]
