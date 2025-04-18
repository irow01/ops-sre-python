from rest_framework.viewsets import GenericViewSet
from rest_framework import status
from rest_framework.mixins import ListModelMixin, CreateModelMixin, RetrieveModelMixin, UpdateModelMixin, \
    DestroyModelMixin
from user.models import User
from .models import Project, SubProject, WorkOrder, WorkOrderData
from .serializer import ProjectSerializer, SubProjectSerializer, WorkOrderSerializer, WorkOrderDataSerializer
from utils.Response import APIResponse
from system.workflow import Workflow, Status, WorkType, OrderRolePermission
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework_jwt.authentication import jwt_decode_handler
from django.core.cache import cache
from utils import jenkinsModel, paginations, SendMail
import json, time


class ProjectView(ListModelMixin, CreateModelMixin, DestroyModelMixin, GenericViewSet):
    queryset = Project.objects.filter(is_delete=False)
    pagination_class = paginations.PageNumberPagination
    serializer_class = ProjectSerializer

    def list(self, request, *args, **kwargs):
        jwt_value = request.META.get('HTTP_X_TOKEN')
        uid = jwt_decode_handler(jwt_value)['pk']
        project_list = self.list_project(uid)
        result = {'data_status': None, 'data': None, 'header': None, 'status': None, 'error_msg': None}
        queryset = self.filter_queryset(self.get_queryset()).filter(
            name__contains=request.query_params['name']).order_by('-create_time')
        total = queryset.count()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            result['data_status'] = 20000
            result['data'] = serializer.data
            result['status'] = status.HTTP_200_OK
        else:
            serializer = self.get_serializer(queryset, many=True)
            result['data_status'] = 20000
            result['status'] = status.HTTP_200_OK
            result['data'] = serializer.data

        return APIResponse(data_status=result['data_status'], data=result['data'], status=result['status'],
                           error_msg=result['error_msg'], total=total, projectList=project_list)

    def create(self, request, *args, **kwargs):
        # result = {'data_status': None, 'data': None, 'header': None, 'status': None, 'error_msg': None}
        # serializer = self.get_serializer(data=request.data)
        # serializer.is_valid(raise_exception=True)
        # self.perform_create(serializer)
        # return APIResponse(data_status=result['data_status'], data=result['data'], error_msg=result['error_msg'])

        result = {'data_status': None, 'data': None, 'header': None, 'status': None, 'error_msg': None}
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            result['data_status'] = 20000
            result['status'] = status.HTTP_200_OK
        else:
            result['data_status'] = 40000
            result['status'] = status.HTTP_200_OK
            result['error_msg'] = serializer.errors

        return APIResponse(data_status=result['data_status'], data=result['data'], status=result['status'],
                           error_msg=result['error_msg'])

    def destroy(self, request, *args, **kwargs):
        """
        单个删除
        删除项目
        接口URL：$HOST/deploy/project/{id}/  方法：delete
        """
        result = {'data_status': None, 'data': None, 'header': None, 'status': None, 'error_msg': None}
        res = Project.objects.filter(id=kwargs['pk']).update(is_delete=True)
        if res:
            result['data_status'] = 20000
            result['status'] = status.HTTP_200_OK
        else:
            result['data_status'] = 40000
            result['status'] = status.HTTP_200_OK
            result['error_msg'] = "删除失败"
        return APIResponse(data_status=result['data_status'], data=result['data'], status=result['status'],
                           error_msg=result['error_msg'])

    def update(self, request, *args, **kwargs):
        """
        单个更新
        更新项目信息
        接口URL：$HOST/deploy/project/{id}/  方法：put/patch
        body：
        {
            "name": "biz",
            "shortName":'biz',
            "describe": "描述",
        }
        """
        result = {'data_status': None, 'data': None, 'header': None, 'status': None, 'error_msg': None}
        queryset_obj = Project.objects.filter(id=kwargs['pk']).first()
        serializer = self.get_serializer(instance=queryset_obj, data=request.data, many=False)
        if serializer.is_valid():
            serializer.update(instance=queryset_obj, validated_data=request.data)
            result['data_status'] = 20000
            result['status'] = status.HTTP_200_OK
        else:
            result['data_status'] = 40000
            result['status'] = status.HTTP_200_OK
            result['error_msg'] = serializer.errors

        return APIResponse(data_status=result['data_status'], data=result['data'], status=result['status'],
                           error_msg=result['error_msg'])

    def retrieve(self, request, *args, **kwargs):
        """
        查询某个ID的项目信息
        接口URL：$HOST/deploy/project/id/  方法：OPTIONS
         body：
            {
                "name": "biz",
                "shortName":'biz',
                "describe": "描述",
            }
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        result = {'data_status': None, 'data': None, 'header': None, 'status': None, 'error_msg': None}
        serializer = self.get_serializer(self.get_object())
        if serializer:
            result['data_status'] = 20000
            result['status'] = status.HTTP_200_OK
            result['data'] = serializer.data
        else:
            result['data_status'] = 40000
            result['status'] = status.HTTP_200_OK
            result['error_msg'] = serializer.errors
        return APIResponse(data_status=result['data_status'], data=result['data'], status=result['status'],
                           error_msg=result['error_msg'])

    @staticmethod
    def list_project(uid):
        """
        列出当前用户是项目经理的所有项目id
        列出当前用户是有权限的所有项目id
        :param :uid 当前用户ID
        :return:{}
        """
        result = {'manage_list': [], 'all_list': [], 'all_list_id': []}
        pid_list = OrderRolePermission.objects.filter(uid=uid, work_type__code='deploy', role__name='项目经理') \
            .values('pid').all()
        all_pid_list = OrderRolePermission.objects.filter(uid=uid, work_type__code='deploy') \
            .values('pid').all().distinct()
        for res in pid_list:
            result['manage_list'].append(res['pid'])
        for item in all_pid_list:
            pid_name = Project.objects.filter(id=item['pid']).values('id', 'name').first()
            result['all_list'].append(pid_name)
            result['all_list_id'].append(item['pid'])
        return result


class SubProjectView(ListModelMixin, CreateModelMixin, GenericViewSet):
    queryset = SubProject.objects.filter(is_delete=False)
    pagination_class = paginations.PageNumberPagination
    serializer_class = SubProjectSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('project', 'env')

    def list(self, request, *args, **kwargs):
        """
        获取子项目列表
        接口URL：$HOST/deploy/subProject/  方法：get
        body：
        {
          "ConfigCenter": "配置文件"
          "PackageName":"编译target目录"
          "ProjectName": "子项目目录"
          "ansible_group": "ansible主机组名称"
          "command": "子项目编译命令"
          "describe":"子项目描述"
          "domain": "访问域名"
          "env": 1
          "environment":"预生产环境"
          "git_address": "git地址"
          "interface_name": "接口名称"
          "job_name":"子项目名称"
          "label": "maven编译标签"
          "name": "base"
          "project": 1
          type:2
          "webapp_dir":"代码存放目录"
        }
        """
        result = {'data_status': None, 'data': None, 'header': None, 'status': None, 'error_msg': None}
        queryset = self.filter_queryset(self.get_queryset()).order_by('-create_time')
        total = queryset.count()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            result['data_status'] = 20000
            result['data'] = serializer.data
            result['status'] = status.HTTP_200_OK
        else:
            serializer = self.get_serializer(queryset, many=True)
            result['data_status'] = 40000
            result['status'] = status.HTTP_200_OK
            result['data'] = serializer.data

        return APIResponse(data_status=result['data_status'], data=result['data'], status=result['status'],
                           error_msg=result['error_msg'], total=total)

    def create(self, request, *args, **kwargs):
        """
        创建子项目
        接口URL：$HOST/deploy/subProject/  方法：POST
        body：
        {
          "ConfigCenter": "配置文件"
          "PackageName":"编译target目录"
          "ProjectName": "子项目目录"
          "ansible_group": "ansible主机组名称"
          "command": "子项目编译命令"
          "describe":"子项目描述"
          "domain": "访问域名"
          "env": 1
          "environment":"预生产环境"
          "git_address": "git地址"
          "interface_name": "接口名称"
          "job_name":"子项目名称"
          "label": "maven编译标签"
          "name": "base"
          "project": 1
          type:2
          "webapp_dir":"代码存放目录"
        }
        """
        result = {'data_status': None, 'data': None, 'header': None, 'status': None, 'error_msg': None}
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            result['data_status'] = 20000
            result['status'] = status.HTTP_200_OK
        else:
            result['data_status'] = 40000
            result['status'] = status.HTTP_200_OK
            result['error_msg'] = serializer.errors

        return APIResponse(data_status=result['data_status'], data=result['data'], status=result['status'],
                           error_msg=result['error_msg'])

    def destroy(self, request, *args, **kwargs):
        """
        单个子项目删除
        接口URL：$HOST/deploy/subProject/id/  方法：delete
        """
        result = {'data_status': None, 'data': None, 'header': None, 'status': None, 'error_msg': None}
        res = self.get_queryset().filter(id=kwargs['pk']).update(is_delete=True)
        if res:
            result['data_status'] = 20000
            result['status'] = status.HTTP_200_OK
        else:
            result['data_status'] = 40000
            result['status'] = status.HTTP_200_OK
            result['error_msg'] = "删除失败"
        return APIResponse(data_status=result['data_status'], data=result['data'], status=result['status'],
                           error_msg=result['error_msg'])

    def update(self, request, *args, **kwargs):
        """
        单个更新
        更新子项目信息
        接口URL：$HOST/deploy/subProject/id/ 方法：put/patch
        body：
        {
          "ConfigCenter": "配置文件"
          "PackageName":"编译target目录"
          "ProjectName": "子项目目录"
          "ansible_group": "ansible主机组名称"
          "command": "子项目编译命令"
          "describe":"子项目描述"
          "domain": "访问域名"
          "env": 1
          "environment":"预生产环境"
          "git_address": "git地址"
          "interface_name": "接口名称"
          "job_name":"子项目名称"
          "label": "maven编译标签"
          "name": "base"
          "project": 1
          "type":2
          "webapp_dir":"代码存放目录"
        }
        """
        result = {'data_status': None, 'data': None, 'header': None, 'status': None, 'error_msg': None}
        queryset_obj = self.get_queryset().filter(id=kwargs['pk']).first()
        serializer = self.get_serializer(instance=queryset_obj, data=request.data, many=False)
        if serializer.is_valid():
            serializer.update(instance=queryset_obj, validated_data=request.data)
            result['data_status'] = 20000
            result['status'] = status.HTTP_200_OK
        else:
            result['data_status'] = 40000
            result['status'] = status.HTTP_200_OK
            result['error_msg'] = serializer.errors
        return APIResponse(data_status=result['data_status'], data=result['data'], status=result['status'],
                           error_msg=result['error_msg'])


class WorkOrderView(ListModelMixin, CreateModelMixin, UpdateModelMixin, DestroyModelMixin, GenericViewSet,
                    RetrieveModelMixin):
    queryset = WorkOrder.objects.filter(is_delete=False)
    serializer_class = WorkOrderSerializer
    pagination_class = paginations.PageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('pid',)

    def create(self, request, *args, **kwargs):
        """
        添加发布工单
        接口URL：$HOST/deploy/workOrder/  方法：POST
        body：
        {
            "synopsis": "概要",
            "pid": "2",
            "proposer":"申请人",
            "operator":"经办人",
            "describe":"描述",
            "environment":"1",
            "priority":"1",
            "current_state_id":"申请",
            "manual_tags":"false",
            "released_list":"jobs1,jobs2",

        }
        """
        result = {'data_status': None, 'data': None, 'header': None, 'status': None, 'error_msg': None}
        request.data['released_list'] = ','.join(str(v) for v in request.data['released_list'])
        res = self.opinion_create(request.data)
        is_not_complete = self.order_whether_complete(request.data)
        if is_not_complete:
            result['data_status'] = 40000
            result['status'] = status.HTTP_200_OK
            result['error_msg'] = '同项目下有工单未完成!'
        elif res['status']:
            serializer = self.get_serializer(data=res['data'])
            if serializer.is_valid():
                self.perform_update(serializer)
                result['data_status'] = 20000
                result['status'] = status.HTTP_200_OK
                self.insert_order_log(res, serializer.data['id'])
            else:
                result['data_status'] = 40000
                result['status'] = status.HTTP_200_OK
                result['error_msg'] = '请确认该项目的产品经理或测试人员是否设置！'
        else:
            result['data_status'] = 40000
            result['status'] = status.HTTP_200_OK
            result['error_msg'] = res['error_msg']
        return APIResponse(data_status=result['data_status'], data=result['data'], status=result['status'],
                           error_msg=result['error_msg'])

    def list(self, request, *args, **kwargs):
        """
        添加工作流状态
        接口URL：$HOST/deploy/workOrder/  方法：get
        body：
        {
            "synopsis": "概要",
            "pid": "2",
            "proposer":"申请人",
            "operator":"经办人",
            "describe":"描述",
            "environment":"1",
            "priority":"1",
            "current_state_id":"申请",
            "manual_tags":"false",
            "released_list":"jobs1,jobs2",
            "current_state_type":"正常"
        }
        """
        jwt_value = request.META.get('HTTP_X_TOKEN')
        uid = jwt_decode_handler(jwt_value)['pk']
        result = {'data_status': None, 'data': None, 'header': None, 'status': None, 'error_msg': None}
        title = \
            {
                'synopsis': '概要',
                'proposer': '申请人',
                "operator": "经办人",
                "environment": "发布环境",
                "current_state_id": "状态",
                "create_time": "申请时间",
                "priority": "优先级",
                "project_name": "项目名称",
            }
        if request.GET.get('statusType'):
            status_list = self.get_status_list(request.GET.get('statusType'))
            query_set = WorkOrder.objects.filter(is_delete=False, current_state_id__in=status_list).order_by(
                '-create_time')
        else:
            query_set = self.get_queryset().order_by('-create_time')
        project_list = self.list_project(uid)
        if request.GET.get('pid') or self.is_not_supper(jwt_decode_handler(jwt_value)['role_name']):
            queryset = self.filter_queryset(query_set)
        else:
            queryset = query_set.filter(pid__in=project_list['all_list_id']).order_by(
                '-create_time')
        total = queryset.count()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            result['data_status'] = 20000
            result['data'] = serializer.data
            result['status'] = status.HTTP_200_OK
        else:
            serializer = self.get_serializer(queryset, many=True)
            result['data_status'] = 20000
            result['status'] = status.HTTP_200_OK
            result['data'] = serializer.data

        return APIResponse(data_status=result['data_status'], data=result['data'], status=result['status'],
                           error_msg=result['error_msg'], title=title, total=total, projectList=project_list)

    def retrieve(self, request, *args, **kwargs):
        """
        查询某个发布工单的信息
        接口URL：$HOST/deploy/workOrder/id/  方法：OPTIONS
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        jwt_value = request.META.get('HTTP_X_TOKEN')
        uid = jwt_decode_handler(jwt_value)['pk']
        result = {'data_status': None, 'data': None, 'header': None, 'status': None, 'error_msg': None}
        serializer = self.get_serializer(self.get_object())
        if serializer:
            result['data_status'] = 20000
            result['status'] = status.HTTP_200_OK
            result['data'] = serializer.data
            workflow = Workflow(uid, 'deploy', serializer.data['pid'], serializer.data['current_state_id'])
            res = workflow.select_permission()
            result['data']['permission'] = res['status']
            if res['status']:
                result['data']['action'] = []
                for item in res['data']:
                    result['data']['action'].append(item['action_name'])
        else:
            result['data_status'] = 40000
            result['status'] = status.HTTP_200_OK
            result['error_msg'] = serializer.errors
        return APIResponse(data_status=result['data_status'], data=result['data'], status=result['status'],
                           error_msg=result['error_msg'])

    def destroy(self, request, *args, **kwargs):
        """
        单个工单删除
        接口URL：$HOST/deploy/workOrder/id/  方法：delete
        """
        result = {'data_status': None, 'data': None, 'header': None, 'status': None, 'error_msg': None}
        res = self.get_queryset().filter(id=kwargs['pk']).update(is_delete=True)
        if res:
            result['data_status'] = 20000
            result['status'] = status.HTTP_200_OK
        else:
            result['data_status'] = 40000
            result['status'] = status.HTTP_200_OK
            result['error_msg'] = "删除失败"
        return APIResponse(data_status=result['data_status'], data=result['data'], status=result['status'],
                           error_msg=result['error_msg'])

    def update(self, request, *args, **kwargs):
        """
        单个更新
        更新工作流名称信息
        接口URL：$HOST/deploy/workOrder/id/ 方法：put/patch
        body：
        {
            "synopsis": "概要",
            "pid": "2",
            "proposer":"申请人",
            "operator":"经办人",
            "describe":"描述",
            "environment":"1",
            "priority":"1",
            "current_state_id":"申请",
            "manual_tags":"false",
            "released_list":"jobs1,jobs2",

        }
        """
        result = {'data_status': None, 'data': None, 'header': None, 'status': None, 'error_msg': None}
        request.data['released_list'] = ','.join(str(v) for v in request.data['released_list'])
        action_type = request.data['action_type'] if request.data['action_type'] else 1
        next_step_data = Workflow(request.data['uid'], request.data['code'],
                                  request.data['pid'], request.data['current_state_id'], action_type)
        res = next_step_data.get_next_data()
        if res['status']:
            request.data['current_state_id'] = res['data'][0]['next_state']
            request.data['operator'] = res['data'][0]['operator'] if res['data'][0]['operator'] else request.data[
                'proposer']
            queryset_obj = WorkOrder.objects.filter(id=kwargs['pk']).first()
            serializer = self.get_serializer(instance=queryset_obj, data=request.data, many=False)
            if serializer.is_valid():
                serializer.update(instance=queryset_obj, validated_data=request.data)
                result['data_status'] = 20000
                result['status'] = status.HTTP_200_OK
            else:
                result['data_status'] = 40000
                result['status'] = status.HTTP_200_OK
                result['error_msg'] = serializer.errors
        else:
            result['data_status'] = 40000
            result['status'] = status.HTTP_200_OK
            result['error_msg'] = res['message']
        return APIResponse(data_status=result['data_status'], data=result['data'], status=result['status'],
                           error_msg=result['error_msg'])

    @staticmethod
    def opinion_create(data):
        """
        获取工单申请后自动按照流程走到下一步的数据
        :param data:
        :return:
        """
        result = {'data': None, 'header': None, 'status': False, 'error_msg': None, 'form_data': None}
        form_data = {'begin_status': None,
                     'after_status': None,
                     'begin_operator': data['proposer'],
                     'operator': data['proposer'],
                     'after_operator': None,
                     'order_id': None,
                     }
        next_step_data = Workflow(data['uid'], data['code'],
                                  data['pid'], data['current_state_id'])

        res = next_step_data.get_next_data()
        if res['status']:
            data['current_state_id'] = res['data'][0]['next_state']
            data['operator'] = res['data'][0]['operator']
            form_data['after_operator'] = res['data'][0]['operator']
            form_data['after_status'] = res['data'][0]['next_state']
            form_data['begin_status'] = res['data'][0]['begin_state']
            result['data'] = data
            result['status'] = res['status']
            result['form_data'] = form_data
        return result

    @staticmethod
    def order_whether_complete(data):
        """
        同项目下的工单是否有未完成的；
        :param data:申请工单的详细信息
        :return:True/False
        """
        process_id = WorkType.objects.filter(code='deploy').values('processId').first()['processId']
        status_list = Status.objects.filter(state_type__in=[1, 2], process_id=process_id).values('status').all()
        result = WorkOrder.objects.filter(pid=data['pid'], is_delete=False, current_state_id__in=status_list).exists()
        return result

    @staticmethod
    def list_project(uid):
        """
        列出当前用户是项目经理的所有项目id
        列出当前用户是有权限的所有项目id
        :param :uid 当前用户ID
        :return:{}
        """
        result = {'manage_list': [], 'all_list': [], 'all_list_id': []}
        pid_list = OrderRolePermission.objects.filter(uid=uid, work_type__code='deploy', role__name='项目经理') \
            .values('pid').all()
        all_pid_list = OrderRolePermission.objects.filter(uid=uid, work_type__code='deploy') \
            .values('pid').all().distinct()
        for res in pid_list:
            result['manage_list'].append(res['pid'])
        for item in all_pid_list:
            pid_name = Project.objects.filter(id=item['pid']).values('id', 'name').first()
            result['all_list'].append(pid_name)
            result['all_list_id'].append(item['pid'])
        return result

    @staticmethod
    def insert_order_log(data, order_id):
        """
        申请操作记录写入数据库
        :param order_id: 工单ID
        :param data:
        {'data':
            {'synopsis': '阿达',
            'pid': '1',
            'environment': '1',
            'priority': '2',
            'manual_tags': False,
            'released_list': '测试2',
            'current_state_id': '待测试审批',
            'describe': '啊',
            'proposer': '熊文涛',
            'workForm': {'uid': 1,
                         'work_type': 1,
                         'code': 'deploy'
                         },
            'operator': '魏旭升,熊文涛'
            },
        'header': None,
        'status': True,
        'error_msg': None,
        'form_data': {'begin_status': '申请',
                      'after_status': '待测试审批',
                      'begin_operator': '熊文涛',
                      'operator': '熊文涛',
                      'after_operator': '魏旭升,熊文涛',
                      'order_id': None
                      }
        }

        :return:工单日志的ID，判断日志是否插入数据库
        """
        data['order_id'] = order_id
        data['operator'] = data['form_data']['operator']
        data['desc'] = data['form_data']['begin_status']
        data['after_status'] = data['form_data']['after_status']
        work_order = WorkOrderDataView()
        work_order.mail_format(data)
        WorkOrderData.objects.create(begin_status=data['form_data']['begin_status'],
                                     after_status=data['form_data']['after_status'],
                                     begin_operator=data['form_data']['begin_operator'],
                                     operator=data['form_data']['operator'],
                                     after_operator=data['form_data']['after_operator'],
                                     order_id_id=order_id,
                                     note=data['form_data']['begin_status'],
                                     desc=data['form_data']['begin_status'])

    @staticmethod
    def get_status_list(data):
        """
        查询工单的某个状态类型下所有状态，列表过滤使用。例如下：
        处理中（正常）：测试审批中，发布中等
        已关闭（关闭）：关闭工单
        :param data:
        :return:
        """
        process_id = WorkType.objects.filter(code='deploy').values('processId').first()['processId']
        result = Status.objects.filter(state_type=data, process_id=process_id).values('status').all()
        return result

    @staticmethod
    def is_not_supper(data):
        """
        判断用户是否为超级管理员,是管理员返回True，否则返回False
        :param data: ['develop','rolesName']
        :return: True/False
        """
        result = False
        if 'supper' in data:
            result = True
        return result


class WorkOrderDataView(ListModelMixin, CreateModelMixin, UpdateModelMixin, GenericViewSet):
    queryset = WorkOrderData.objects.filter(is_delete=False)
    serializer_class = WorkOrderDataSerializer

    def create(self, request, *args, **kwargs):
        """
        添加发布工单日志数据
        接口URL：$HOST/deploy/WorkOrderData/  方法：POST
        body：
        {
            "order_id": "工单id",
            "begin_status": "变更前状态",
            "after_status":"变更后状态",
            "begin_operator":"变更前经办人",
            "after_operator":"变更后经办人",
            "operator":"实际经办人",
            "desc":"备注信息",
            "note":"状态标题",
        }
        """
        result = {'data_status': None, 'data': None, 'header': None, 'status': None, 'error_msg': None}
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            result['data_status'] = 20000
            result['status'] = status.HTTP_200_OK
            self.mail_format(serializer.data)
        else:
            result['data_status'] = 40000
            result['status'] = status.HTTP_200_OK
            result['error_msg'] = serializer.errors

        return APIResponse(data_status=result['data_status'], data=result['data'], status=result['status'],
                           error_msg=result['error_msg'])

    def list(self, request, *args, **kwargs):
        """
        添加工作流状态
        接口URL：$HOST/deploy/WorkOrderData/  方法：get
        body：
        {
            "order_id": "工单id",
            "begin_status": "变更前状态",
            "after_status":"变更后状态",
            "begin_operator":"变更前经办人",
            "after_operator":"变更后经办人",
            "operator":"实际经办人",
            "note":"备注信息",
        }
        """
        result = {'data_status': None, 'data': None, 'header': None, 'status': None, 'error_msg': None}
        queryset = self.filter_queryset(self.get_queryset()).filter(order_id=request.query_params['order_id']).all()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            result['data_status'] = 20000
            result['data'] = serializer.data
            result['status'] = status.HTTP_200_OK
        else:
            serializer = self.get_serializer(queryset, many=True)
            result['data_status'] = 20000
            result['status'] = status.HTTP_200_OK
            result['data'] = serializer.data

        return APIResponse(data_status=result['data_status'], data=result['data'], status=result['status'],
                           error_msg=result['error_msg'])

    def mail_format(self, data):
        """
        数据整理好，然后以邮件形式发送
        :param data: 工单数据
        """
        result = {'content': data, 'to_mail': [], 'sub': None}
        env = {1: '预生产环境', 2: '生产环境'}
        res = WorkOrder.objects.filter(id=data['order_id'], is_delete=False).values('pid__name', 'pid_id', 'describe',
                                                                                    'environment', 'released_list',
                                                                                    'synopsis', 'operator',
                                                                                    'current_state_id').first()
        state_type = self.get_status_type(res['current_state_id'])
        # 获取邮件的内容信息
        result['content']['create_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        result['content']['describe'] = res['describe']
        result['content']['environment'] = env[res['environment']]
        result['content']['released_list'] = res['released_list']
        result['content']['type'] = 'deploy'
        result['sub'] = res['synopsis']
        result['content']['project'] = res['pid__name']
        result['content']['sub'] = res['synopsis']
        result['content']['manager'] = '未指定项目经理'
        result['content']['tester'] = '未指定测试人员'
        result['content']['PM'] = '未指定产品经理'
        result['content']['id'] = data['order_id']
        # 获取邮件内容中的项目经理、测试人员及产品经理等名单
        project_roles_info = OrderRolePermission.objects.filter(pid=res['pid_id'], work_type__code='deploy').values(
            'uid__email', 'role__name', 'uid__nickname').all()
        for item in project_roles_info:
            result['to_mail'].append(item['uid__email'])
            if item['role__name'] == '项目经理':
                result['content']['manager'] = item['uid__nickname']
            elif item['role__name'] == '测试人员':
                result['content']['tester'] = item['uid__nickname']
            elif item['role__name'] == '产品经理':
                result['content']['PM'] = item['uid__nickname']
        # 状态类型为完成或者申请则全体人员收到邮件，否则经办人收到邮件
        if state_type == 3 or state_type == 1:
            result['to_mail'] = set(result['to_mail'])
        else:
            result['to_mail'] = []
            for item in res['operator'].split(','):
                result['to_mail'].append(
                    User.objects.filter(nickname=item, is_delete=False).values('email').first()['email'])
        sm = SendMail.SendMail(result)
        sm.order_send_mail()

    @staticmethod
    def get_status_type(name):
        """
        获取工单状态的类型
        :param name: 工单状态
        :return: 工单类型
        """
        state_type = Status.objects.filter(process_id__worktype__code='deploy', status=name) \
            .values('state_type').first()
        return state_type['state_type']


class JenkinsView(ListModelMixin, CreateModelMixin, RetrieveModelMixin, GenericViewSet):
    result = {'data_status': None, 'data': None, 'header': None, 'status': None, 'error_msg': None}

    def create(self, request, *args, **kwargs):
        """
        Jenkins发布接口
        前端传入字段为: {"pid":PID, "jobs": [{"name":"NAME","args":"ARGS"}, ]
        向redis中生成两个Key:
            plist: 记录了所有工单ID, 格式为: {"pid": [PID,]}
            deploy + pid : {'status': False, 'job_list': [{'JOB_NAME': { 'status': False, 'JOB_ID': 0}}, ]}

        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        pid = request.data.get("pid")
        jobs = request.data.get("jobs")
        plist = cache.get("plist")  # 获取redis中pid list
        deploy_dict = cache.get("deploy" + str(pid))

        Jk = jenkinsModel.JenkinsModel()

        # 生成deploy + pid的redis键
        if deploy_dict is None:
            deploy_dict = {"pid": str(pid), "status": False}
            job_list = {}
            for job in jobs:
                last_build_number = Jk.get_last_completed_build_number(job["name"])
                job_list[job["name"]] = {"status": 0, "job_id": 0, "last_build_number": last_build_number}
            deploy_dict["job_list"] = job_list
        else:
            deploy_dict = json.loads(deploy_dict)
            for job in jobs:
                if deploy_dict['job_list'].get(job["name"]):
                    deploy_dict['status'] = False
                    deploy_dict['job_list'][job["name"]]['status'] = 0
                else:
                    deploy_dict['job_list'][job["name"]] = {"status": 0, "job_id": 0}

        for job in jobs:
            if len(job["args"]) == 0:
                queue_id = Jk.build_job(job["name"])
            else:
                queue_id = Jk.build_job(job["name"])

            deploy_dict['job_list'][job["name"]]['job_id'] = queue_id

        if plist is None:
            plist = {"pid": [str(pid), ]}

            if cache.set("lock", "true", nx=True, timeout=1):
                cache.set("plist", json.dumps(plist), timeout=None)
                cache.set("deploy" + str(pid), json.dumps(deploy_dict), timeout=None)
                self.result["error_msg"] = "ok"
                self.result["data_status"] = status.HTTP_200_OK
            else:
                self.result["error_msg"] = "业务冲突,请重试"
                self.result["data_status"] = status.HTTP_504_GATEWAY_TIMEOUT

        else:
            plist = json.loads(plist)
            if pid not in plist['pid']:
                plist["pid"].append(pid)

            if cache.set("lock", "true", nx=True, timeout=1):
                cache.set("plist", json.dumps(plist), timeout=None)
                cache.set("deploy" + str(pid), json.dumps(deploy_dict), timeout=None)
                self.result["error_msg"] = "ok"
                self.result["data_status"] = status.HTTP_200_OK
            else:
                self.result["error_msg"] = "业务冲突,请重试"
                self.result["data_status"] = status.HTTP_504_GATEWAY_TIMEOUT

        return APIResponse(data_status=self.result['data_status'], data=self.result['data'],
                           error_msg=self.result['error_msg'])

    def list(self, request, *args, **kwargs):
        pid = request.query_params.get('pid', 0)
        job_list = {}
        if pid != 0:
            deploy_str = cache.get("deploy" + str(pid))
            if deploy_str is not None:
                deploy_dict = json.loads(deploy_str)
                job_dict = deploy_dict['job_list']
                for job_name, job_status in job_dict.items():
                    job_list[job_name] = job_status

                self.result['data'] = job_list
                self.result['data_status'] = status.HTTP_200_OK
            else:
                self.result['error_msg'] = '工单未查询到'
                self.result['data_status'] = status.HTTP_400_BAD_REQUEST
                self.result['data'] = None

        return APIResponse(data_status=self.result['data_status'], data=self.result['data'],
                           error_msg=self.result['error_msg'])

    def retrieve(self, request, *args, **kwargs):
        """
        获取指定Jenkins Job的日志
        接口URL：$HOST/deploy/jenkins/JOB_NAME?id=ID  方法：OPTIONS
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        job_name = kwargs['pk']
        #build_id = request.query_params.get('id')
        JK = jenkinsModel.JenkinsModel()
        info = JK.get_build_console_output(job_name)
        if info:
            self.result['data'] = info
            self.result['data_status'] = 2000
            self.result['error_msg'] = ''
        else:
            self.result['data'] = ''
            self.result['data_status'] = 4000
            self.result['error_msg'] = 'Build Id不存在'
        return APIResponse(data_status=self.result['data_status'], data=self.result['data'],
                           error_msg=self.result['error_msg'])
