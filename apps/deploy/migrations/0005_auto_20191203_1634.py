# Generated by Django 2.1.7 on 2019-12-03 08:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('deploy', '0004_auto_20191203_1610'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subproject',
            name='ansible_group',
            field=models.CharField(max_length=64, null=True, verbose_name='ansible主机组名称'),
        ),
    ]
