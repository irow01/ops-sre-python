# Generated by Django 2.1.7 on 2020-03-26 06:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('deploy', '0011_subproject_domain'),
    ]

    operations = [
        migrations.AddField(
            model_name='workorderdata',
            name='desc',
            field=models.CharField(blank=True, max_length=512, verbose_name='备注信息'),
        ),
        migrations.AlterField(
            model_name='workorderdata',
            name='note',
            field=models.CharField(blank=True, max_length=20, verbose_name='状态标题'),
        ),
    ]
