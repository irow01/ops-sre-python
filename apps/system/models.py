from django.db import models
from utils.BaseModel import BaseModel
from user.models import User


class RoleGroup(BaseModel):
    """
    项目角色组
    """
    name = models.CharField(verbose_name='项目角色组', max_length=64)
    description = models.CharField(max_length=100, verbose_name='项目角色组描述', blank=True)


class Role(BaseModel):
    """
    项目角色
    """
    name = models.CharField(verbose_name='项目角色', max_length=64)


class Group2Roles(BaseModel):
    """
    角色与角色组关联表
    """
    gid = models.ForeignKey(RoleGroup, on_delete=models.CASCADE, verbose_name="角色组")
    rid = models.ForeignKey(Role, on_delete=models.CASCADE, verbose_name="角色")


class Process(BaseModel):
    """
    工作流程表
    """
    name = models.CharField(max_length=32, verbose_name='流程标识', unique=True)
    state = models.BooleanField(default=True, verbose_name='流程状态')
    description = models.CharField(max_length=100, verbose_name='流程描述', blank=True)
    role_group = models.IntegerField(verbose_name='项目角色组id')

    class Meta:
        verbose_name_plural = '工作流程表'

    def __str__(self):
        return self.name


class Status(BaseModel):
    """
    工作状态表
    工作流中的不同状态各有不同的属性类型, 在此总结出几种常见的状态类型枚举:
    开始(start)：每个进程只应该一个。此状态是创建新请求时所处的状态。
    正常(normal)：没有特殊名称的常规状态。
    完成(complete)：表示此状态下的任何请求已正常完成的状态。
    拒绝(denied)：表示此状态下的任何请求已被拒绝的状态（例如，从未开始且不会被处理）。
    已取消(cancelled)：表示此状态下的任何请求已被取消的状态（例如，工作已开始但尚未完成）。
    """
    process_id = models.ForeignKey(Process, on_delete=models.CASCADE, verbose_name='所属流程的id')
    status = models.CharField(max_length=32, verbose_name='工作流状态')
    type = (
        (1, "开始"),
        (2, "正常"),
        (3, "完成"),
        (4, "拒绝"),
        (5, "已取消"),
    )
    state_type = models.SmallIntegerField(choices=type, default=1, verbose_name="状态类型")
    description = models.CharField(max_length=32, verbose_name='状态描述')

    class Meta:
        verbose_name_plural = '工作状态表'


class Action(BaseModel):
    """
    工作流操作表
    同样的不同的动作也各有不同的属性类型, 在此总结出几种常见的动作类型枚举:
    批准(approve)：操作人将请求应移至下一个状态。
    拒绝(deny)：操作人将请求应移至上一个状态。
    取消(cancel)：操作人将请求应在此过程中移至“已取消”状态。
    重新启动(restart)：操作人将将请求移回到进程中的“开始”状态。
    解决(resolve)：操作人将将请求一直移动到Completed状态。
    """
    process_id = models.ForeignKey(Process, on_delete=models.CASCADE, verbose_name='所属流程的id')
    status = models.CharField(max_length=32, verbose_name='工作流状态')
    type = (
        (1, "批准"),
        (2, "拒绝"),
        (3, "取消"),
        (4, "重新启动"),
        (5, "解决"),
    )
    action_type = models.SmallIntegerField(choices=type, default=1, verbose_name="状态类型")
    description = models.CharField(max_length=32, verbose_name='状态描述')

    class Meta:
        verbose_name_plural = '工作状态表'


class Transition(BaseModel):
    """
    工作转换表
    """
    process_id = models.ForeignKey(Process, on_delete=models.CASCADE, verbose_name='所属流程的id')
    current_state_id = models.IntegerField(verbose_name='当前状态id')
    next_state_id = models.IntegerField(verbose_name='下一状态id')
    action_id = models.IntegerField(verbose_name='所属流程操作id')
    roles_list = models.CharField(max_length=30, verbose_name="有权限执行的角色列表", default="")

    class Meta:
        verbose_name_plural = '工作流转表'


class WorkType(BaseModel):
    """
    工单类型基础表
    code：工单类型编号，在需要使用工作流的工单后端代码写死
    """
    type = models.CharField(max_length=30, verbose_name="请求类型", unique=True)
    processId = models.ForeignKey(Process, on_delete=models.CASCADE, verbose_name="工作流表")
    code = models.CharField(max_length=30, verbose_name="请求类型code", unique=True)


class OrderRolePermission(models.Model):
    """
    工单角色权限分配表
    pid:当work_type为编号deploy，此字段才被赋值（项目ID）。其他work_type值为''

    """
    role = models.ForeignKey(Role, on_delete=models.CASCADE, verbose_name="工单角色")
    pid = models.IntegerField(verbose_name='所属项目id', default='')
    uid = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")
    work_type = models.ForeignKey(WorkType, on_delete=models.CASCADE, verbose_name="工单类型")

