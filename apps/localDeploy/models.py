from django.db import models
from utils.BaseModel import BaseModel
from system.models import WorkType


class LocalProject(BaseModel):
    """
    本地化项目表
    """
    name = models.CharField(verbose_name='企业名称', max_length=32, unique=True)
    tag = (
        (1, "定制化项目"),
        (2, "标准化项目"),
    )
    projectTags = models.SmallIntegerField(choices=tag, default=1, verbose_name="项目类型")
    describe = models.TextField(verbose_name='项目描述')
    companyCode = models.CharField(verbose_name='企业编号', max_length=32, default="", blank=True)

    class Meta:
        verbose_name_plural = '项目信息表'

    def __str__(self):
        return self.name


class LocalOrder(BaseModel):
    """
    发布项目表
    """
    patch = models.CharField(verbose_name='概要', max_length=20, default=0)
    synopsis = models.CharField(verbose_name='概要', max_length=32)
    pid = models.ForeignKey(LocalProject, on_delete=models.CASCADE, verbose_name="项目id")
    operator = models.CharField(verbose_name='经办人', max_length=20, default="")
    proposer = models.CharField(verbose_name='申请人', max_length=20, default="")
    describe = models.TextField(verbose_name='描述')
    tag = (
        (1, "定制化发布"),
        (2, "标准化发布"),
    )
    deployTags = models.SmallIntegerField(choices=tag, default=1, verbose_name="发布类型")
    priority_list = (
        (1, "低"),
        (2, "中等"),
        (3, "高"),
        (4, "紧急"),
    )
    priority = models.SmallIntegerField(choices=priority_list, default=1, verbose_name="优先级")
    current_state_id = models.CharField(verbose_name='当前状态', max_length=20, default="")
    backup_mirror_url = models.CharField(verbose_name='整合镜像包', max_length=150, default="null")

    class Meta:
        verbose_name_plural = '工单表'


class LocalOrderData(BaseModel):
    """
    本地化发布工作流请求日志表
    """
    order_id = models.ForeignKey(LocalOrder, on_delete=models.CASCADE, verbose_name='工单id')
    begin_status = models.CharField(verbose_name='变更前状态', max_length=20, default="")
    after_status = models.CharField(verbose_name='变更后状态', max_length=20, default="")
    begin_operator = models.CharField(verbose_name='变更前经办人', max_length=20, default="")
    after_operator = models.CharField(verbose_name='变更后经办人', max_length=20, default="")
    operator = models.CharField(verbose_name='实际经办人', max_length=20, default="")
    desc = models.CharField(verbose_name='备注信息', max_length=512, blank=True)
    note = models.CharField(verbose_name='状态标题', max_length=20, blank=True)
