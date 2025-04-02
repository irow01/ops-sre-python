from django.db import models
from utils.BaseModel import BaseModel
from uuid import uuid4


class User(BaseModel):
    """
    用户表：用户信息
    """
    username = models.CharField(verbose_name='用户名', max_length=32, unique=True)
    nickname = models.CharField(verbose_name='昵称', max_length=32)
    email = models.EmailField(verbose_name='邮箱', unique=True)
    last_login_time = models.DateTimeField(verbose_name='最后登入时间', auto_now=True)
    last_login_ip = models.CharField(max_length=20, verbose_name='上次登入IP', null=True)
    phone = models.CharField(max_length=11, verbose_name='手机号', null=True)
    department = models.CharField(verbose_name="部门", max_length=32, null=True)
    Gender = (
        (1, "男"),
        (2, "女"),
    )
    gender = models.SmallIntegerField(choices=Gender, default=1, verbose_name="性别")
    avatar = models.FileField(upload_to='avatar', default='avatar/default.jpeg')
    account_expr = models.DateField(null=True, verbose_name='密码过期时间')
    is_supper = models.BooleanField(default=False, verbose_name='超级管理员')
    role = models.ManyToManyField(to='Role', related_name='role', verbose_name='角色')
    uuid = models.UUIDField(default=uuid4(), verbose_name='用户JWT密钥')

    class Meta:
        verbose_name_plural = '用户表'

    def __str__(self):
        return self.nickname

    @property
    def role_name(self):
        res = self.role.all()
        mode_list = []
        for x in res:
            mode_list.append(x.name)

        return mode_list

    @property
    def avatar_url(self):
        host = 'media/'
        url = host + self.avatar.__str__()
        return url


class Role(BaseModel):
    """
    用户角色表
    """
    name = models.CharField(max_length=32, verbose_name='角色名称', null=True)
    desc = models.CharField(max_length=32, verbose_name='角色描述', default='')
    description = models.CharField(max_length=64, verbose_name='描述', default='')
    permission = models.ManyToManyField(to='Permission', verbose_name='权限', blank=True)

    class Meta:
        verbose_name_plural = '角色表'

    def __str__(self):
        return self.name

    def permissions(self):
        permission_list = []
        res = self.permission.all()
        for item in res:
            permission_list.append(item.id)
        return permission_list


class Method(BaseModel):
    """
    请求方法表
    """
    name = models.CharField(max_length=32, unique=True, verbose_name='方法名称')
    action = models.CharField(max_length=32, unique=True, verbose_name='方法')

    class Meta:
        verbose_name_plural = '请求方法表'

    def __str__(self):
        return self.name


class Permission(BaseModel):
    """
    权限表
    """
    name = models.CharField(max_length=32, unique=True, verbose_name='权限名称')
    url = models.CharField(max_length=32, verbose_name='接口地址')
    method = models.ForeignKey(to='Method', related_name='method', on_delete=models.CASCADE, null=True)
    pid = models.ForeignKey('self', verbose_name='父权限', on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name_plural = '权限表'

    def __str__(self):
        return self.name
