# Generated by Django 2.1.7 on 2019-12-13 05:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0013_auto_20191213_1353'),
        ('system', '0012_auto_20191212_1426'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrderRolePermission',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pid', models.IntegerField(default='', verbose_name='所属项目id')),
                ('role', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='system.Role', verbose_name='工单角色')),
                ('uid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.User', verbose_name='用户')),
                ('work_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='system.WorkType', verbose_name='工单类型')),
            ],
        ),
    ]
