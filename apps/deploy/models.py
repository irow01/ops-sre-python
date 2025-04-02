from django.db import models
from utils.BaseModel import BaseModel


class Project(BaseModel):
    """
    项目表
    """
    name = models.CharField(verbose_name='项目名', max_length=32, unique=True)
    shortName = models.CharField(verbose_name='项目简称', max_length=15, unique=True)
    describe = models.TextField(verbose_name='项目描述')
    is_load_balancing = models.BooleanField(default=False, verbose_name='是否负载均衡')

    class Meta:
        verbose_name_plural = '项目信息表'

    def __str__(self):
        return self.name


class SubProject(BaseModel):
    """
    二级项目表
    """
    projectType = (
        (1, "static"),
        (2, "tomcat"),
        (3, "python"),
        (4, "go"),
    )
    name = models.CharField(verbose_name='项目名', max_length=32)
    describe = models.TextField(verbose_name='项目描述')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name='一级项目')
    domain = models.CharField(verbose_name="项目域名", max_length=64, null=True)
    environment = (
        (1, "预生产环境"),
        (2, "生产环境"),
        (3, "测试环境"),
        (4, "开发环境"),
    )
    env = models.SmallIntegerField(choices=environment, default=1, verbose_name="发布环境")
    type = models.SmallIntegerField(choices=projectType, default=2, verbose_name='项目类型', null=False)
    command = models.CharField(verbose_name='项目命令', max_length=512, null=True)
    git_address = models.CharField(verbose_name='git地址', max_length=512, null=True)
    interface_name = models.CharField(verbose_name='接口名称', max_length=32, null=True)
    label = models.CharField(max_length=32, verbose_name='maven编译标签', null=True)
    ConfigCenter = models.CharField(max_length=128, verbose_name='配置中心文件', null=True)
    PackageName = models.CharField(max_length=64, verbose_name='编译target目录', null=True)
    ProjectName = models.CharField(max_length=64, verbose_name='项目目录', null=True)
    webapp_dir = models.CharField(max_length=128, verbose_name='项目存放路径', null=True)
    ansible_group = models.CharField(max_length=64, verbose_name='ansible主机组名称', null=True)


class WorkOrder(BaseModel):
    """
    发布项目表
    """
    synopsis = models.CharField(verbose_name='概要', max_length=32)
    pid = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name="项目id")
    operator = models.CharField(verbose_name='经办人', max_length=20, default="")
    proposer = models.CharField(verbose_name='申请人', max_length=20, default="")
    describe = models.TextField(verbose_name='描述')
    released_list = models.CharField(verbose_name='需要发布的工程', max_length=512)
    env = (
        (1, "预生产环境"),
        (2, "生产环境"),
    )
    environment = models.SmallIntegerField(choices=env, default=1, verbose_name="发布环境")
    manual_tags = models.BooleanField(default=False, verbose_name='手动发布标签')
    priority_list = (
        (1, "低"),
        (2, "中等"),
        (3, "高"),
        (4, "紧急"),
    )
    priority = models.SmallIntegerField(choices=priority_list, default=1, verbose_name="优先级")
    current_state_id = models.CharField(verbose_name='当前状态', max_length=20, default="")

    class Meta:
        verbose_name_plural = '发布工单表'


class WorkOrderData(BaseModel):
    """
    工作流请求日志表
    """
    order_id = models.ForeignKey(WorkOrder, on_delete=models.CASCADE, verbose_name='工单id')
    begin_status = models.CharField(verbose_name='变更前状态', max_length=20, default="")
    after_status = models.CharField(verbose_name='变更后状态', max_length=20, default="")
    begin_operator = models.CharField(verbose_name='变更前经办人', max_length=20, default="")
    after_operator = models.CharField(verbose_name='变更后经办人', max_length=20, default="")
    operator = models.CharField(verbose_name='实际经办人', max_length=20, default="")
    desc = models.CharField(verbose_name='备注信息', max_length=512, blank=True)
    note = models.CharField(verbose_name='状态标题', max_length=20, blank=True)


class JenkinsStatus(BaseModel):
    """
    jenkins任务回写表
    """
    gid = models.CharField(max_length=64, verbose_name='工单id')
    jobs_name = models.CharField(max_length=64, verbose_name='jenkins任务名称')
    build_number = models.IntegerField(verbose_name='jenkins任务构建ID')
    count_number = models.IntegerField(null=True, verbose_name='工单包含的任务数')
    status = models.CharField(max_length=10, null=True, verbose_name='job最终发布状态')

    class Meta:
        verbose_name_plural = 'jobs发布状态表'

    def __str__(self):
        return self.jobs_name


class JenkinsRollback(BaseModel):
    jobs_name = models.CharField(max_length=64, unique=True, verbose_name='jenkins任务名称')
    build_number = models.IntegerField(verbose_name='jenkins最后发布成功的buildID')

    class Meta:
        verbose_name_plural = 'jenkins回滚ID表'

    def __str__(self):
        return self.jobs_name
