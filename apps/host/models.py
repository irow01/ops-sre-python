from django.db import models
from utils.BaseModel import BaseModel
from deploy.models import Project


class HostInfo(BaseModel):
    """
    主机信息表
    """
    name = models.CharField(verbose_name='主机名', max_length=32)
    ip = models.GenericIPAddressField(verbose_name='IP地址', unique=True)
    CPU = models.CharField(verbose_name='cpu', max_length=10, default='')
    memory = models.CharField(verbose_name='内存', max_length=10, default='')
    OSName = models.CharField(verbose_name="操作系统", max_length=30, default='')
    OSType = models.CharField(verbose_name="系统类型", max_length=20, default='')
    environment = (
        (1, "预生产环境"),
        (2, "生产环境"),
        (3, "测试环境"),
        (4, "开发环境"),
    )
    env = models.SmallIntegerField(choices=environment, default=1, verbose_name="主机环境")
    describe = models.CharField(verbose_name="简述", max_length=50, default='')
    sshTag = models.BooleanField(default=True, verbose_name='是否可以用ssh链接')

    class Meta:
        verbose_name_plural = '主机信息表'

    def __str__(self):
        return self.name


class HostToProject(models.Model):
    """
    主机与项目多对多关系表
    """
    hid = models.ForeignKey(HostInfo, on_delete=models.CASCADE, verbose_name="主机ID")
    pid = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name="项目id")


# class HostAccessLog(models.Model):
#     """
#     主机远程操作日志
#     """
#     ip = models.GenericIPAddressField(verbose_name='IP地址', unique=True)
#     nid = models.IntegerField(verbose_name='用户ID', null=False)
#     access_time = models.DateTimeField(verbose_name='访问时间', auto_now_add=True)
#     cmd = models.CharField(verbose_name='操作命令', max_length=255)
#     access_user = models.CharField(verbose_name='操作用户', max_length=10, default='')
#
#     class Meta:
#         verbose_name_plural = 'ssh操作日志表'
#
#     def __str__(self):
#         return self.cmd
