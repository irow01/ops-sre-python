from django.db import models
from utils.BaseModel import BaseModel
from system.models import WorkType


# Create your models here.
class OPSWorkOrder(BaseModel):
    """
    工单表
    """
    synopsis = models.CharField(verbose_name='概要', max_length=32)
    operator = models.CharField(verbose_name='经办人', max_length=20, default="")
    proposer = models.CharField(verbose_name='申请人', max_length=20, default="")
    describe = models.TextField(verbose_name='描述')
    type = models.ForeignKey(WorkType, on_delete=models.CASCADE, verbose_name="工单类型")
    typeList = models.CharField(verbose_name='工单类型列表', max_length=20, default="")
    env = (
        (1, "开发环境"),
        (2, "测试环境"),
        (3, "预生产环境"),
        (4, "生产环境"),
    )
    environment = models.SmallIntegerField(choices=env, default=1, verbose_name="环境")
    priority_list = (
        (1, "低"),
        (2, "中等"),
        (3, "高"),
        (4, "紧急"),
    )
    priority = models.SmallIntegerField(choices=priority_list, default=1, verbose_name="优先级")
    current_state_id = models.CharField(verbose_name='当前状态', max_length=20, default="")

    class Meta:
        verbose_name_plural = '工单表'


class OPSWorkOrderData(BaseModel):
    """
    工作流请求日志表
    """
    order_id = models.ForeignKey(OPSWorkOrder, on_delete=models.CASCADE, verbose_name='工单id')
    begin_status = models.CharField(verbose_name='变更前状态', max_length=20, default="")
    after_status = models.CharField(verbose_name='变更后状态', max_length=20, default="")
    begin_operator = models.CharField(verbose_name='变更前经办人', max_length=20, default="")
    after_operator = models.CharField(verbose_name='变更后经办人', max_length=20, default="")
    operator = models.CharField(verbose_name='实际经办人', max_length=20, default="")
    desc = models.CharField(verbose_name='备注信息', max_length=512, blank=True)
    note = models.CharField(verbose_name='状态标题', max_length=20, blank=True)