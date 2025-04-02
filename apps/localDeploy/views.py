import json

import re
import threading

import requests
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.mixins import ListModelMixin, CreateModelMixin, RetrieveModelMixin, UpdateModelMixin, \
    DestroyModelMixin
from rest_framework.viewsets import GenericViewSet
from rest_framework_jwt.authentication import jwt_decode_handler
from system.BackupImage import Ufile
from system.workflow import Workflow, Status, WorkType, OrderRolePermission
from user.models import User
from utils import paginations, SendMail
from utils.Response import APIResponse
from .models import LocalOrder, LocalOrderData, LocalProject
from .serializer import LocalProjectSerializer, LocalOrderSerializer, LocalOrderDataSerializer


class LocalProjectView(ListModelMixin, CreateModelMixin, DestroyModelMixin, GenericViewSet):
    queryset = LocalProject.objects.filter(is_delete=False)
    pagination_class = paginations.PageNumberPagination
    serializer_class = LocalProjectSerializer

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
        result = {'data_status': None, 'data': None, 'header': None, 'status': None, 'error_msg': None}
        if request.data:
            serializer = self.get_serializer(data=request.data)
        else:
            data = self.get_local_project_list()
            serializer = self.get_serializer(data=data, many=True)
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
        res = LocalProject.objects.filter(id=kwargs['pk']).update(is_delete=True)
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
        queryset_obj = LocalProject.objects.filter(id=kwargs['pk']).first()
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
        pid_list = OrderRolePermission.objects.filter(uid=uid, work_type__code='local', role__name='项目经理') \
            .values('pid').all()
        all_pid_list = OrderRolePermission.objects.filter(uid=uid, work_type__code='local') \
            .values('pid').all().distinct()
        for res in pid_list:
            result['manage_list'].append(res['pid'])
        for item in all_pid_list:
            pid_name = LocalProject.objects.filter(id=item['pid']).values('id', 'name').first()
            result['all_list'].append(pid_name)
            result['all_list_id'].append(item['pid'])
        return result

    def get_local_project_list(self):
        result = []
        url = 'https://api.isesol.com/gateway/basemanagerfront/oplocal/getOpLocalByCompanyName'
        params = {'companyName': ''}
        response = requests.post(url, params)

        # 处理 API 响应
        if response.status_code == 200:
            # 获取 API 响应内容
            data = json.loads(response.text)
            # 处理数据
            for user in data:
                local_project_obj = dict()
                local_project_obj['name'] = user['companyName']
                local_project_obj['companyCode'] = user['companyCode']
                local_project_obj['describe'] = user['companyName']
                if not self.filtration_host_info(local_project_obj['companyCode']):
                    result.append(local_project_obj)
        return result

    @staticmethod
    def filtration_host_info(code):
        """
        判断本地化项目中是否存在companyCode
        :return: list
        """
        return LocalProject.objects.filter(companyCode=code).exists()


class LocalOrderView(ListModelMixin, CreateModelMixin, UpdateModelMixin, DestroyModelMixin, GenericViewSet,
                     RetrieveModelMixin):
    queryset = LocalOrder.objects.filter(is_delete=False)
    serializer_class = LocalOrderSerializer
    pagination_class = paginations.PageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('pid',)

    def create(self, request, *args, **kwargs):
        """
        添加运维工单
        接口URL：$HOST/localDeploy/LocalOrder/  方法：POST
        body：
        {
            "synopsis": "概要",
            "proposer":"申请人",
            "operator":"经办人",
            "describe":"描述",
            "deployTags":"1",
            "priority":"1",
            "current_state_id":"申请",
            "pid":"2"

        }
        """
        result = {'data_status': None, 'data': None, 'header': None, 'status': None, 'error_msg': None}
        is_not_complete = self.order_whether_complete(request.data)
        if is_not_complete:
            result['data_status'] = 40000
            result['status'] = status.HTTP_200_OK
            result['error_msg'] = '同项目下有工单未完成!'
        else:
            res = self.init_request(request.data)
            if res['status']:
                serializer = self.get_serializer(data=res['data'])
                if serializer.is_valid():
                    self.perform_create(serializer)
                    result['data_status'] = 20000
                    result['status'] = status.HTTP_200_OK
                    result['data'] = serializer.data
                    self.insert_order_log(res, serializer.data['id'])
                else:
                    result['data_status'] = 40000
                    result['status'] = status.HTTP_200_OK
                    result['error_msg'] = serializer.errors
            else:
                result['data_status'] = 40000
                result['status'] = status.HTTP_200_OK
                result['error_msg'] = '用户没有权限!'
        return APIResponse(data_status=result['data_status'], data=result['data'], status=result['status'],
                           error_msg=result['error_msg'])

    def list(self, request, *args, **kwargs):
        """
        添加工作流状态
        接口URL：$HOST/localDeploy/LocalOrder/  方法：get
        body：
        {
            "synopsis": "概要",
            "pid": "2",
            "proposer":"申请人",
            "operator":"经办人",
            "describe":"描述",
            "deployTags":"1",
            "priority":"1",
            "current_state_id":"申请",
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
                "deployTags": "发布类型",
                "current_state_id": "状态",
                "create_time": "申请时间",
                "priority": "优先级",
                "project_name": "项目名称",
            }
        if request.GET.get('statusType'):
            status_list = self.get_status_list(request.GET.get('statusType'))
            query_set = LocalOrder.objects.filter(is_delete=False, current_state_id__in=status_list).order_by(
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
        查询运维工单
        接口URL：$HOST/localDeploy/LocalOrder/id/  方法：OPTIONS
        body：
        {
            "synopsis": "概要",
            "proposer":"申请人",
            "operator":"经办人",
            "describe":"描述",
            "deployTags":"1",
            "priority":"1",
            "current_state_id":"申请",
        }
        """
        jwt_value = request.META.get('HTTP_X_TOKEN')
        uid = jwt_decode_handler(jwt_value)['pk']
        result = {'data_status': None, 'data': None, 'header': None, 'status': None, 'error_msg': None}
        serializer = self.get_serializer(self.get_object())
        if serializer:
            result['data_status'] = 20000
            result['status'] = status.HTTP_200_OK
            result['data'] = serializer.data
            workflow = Workflow(uid, 'local', serializer.data['pid'], serializer.data['current_state_id'])
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
        接口URL：$HOST/localDeploy/LocalOrder/id/  方法：delete
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
        接口URL：$HOST/localDeploy/OPSWorkOrder/id/ 方法：put/patch
        body：
        {
            "synopsis": "概要",
            "proposer":"申请人",
            "operator":"经办人",
            "describe":"描述",
            "environment":"1",
            "priority":"1",
            "current_state_id":"申请",
            "type":"2"

        }
        """
        result = {'data_status': None, 'data': None, 'header': None, 'status': None, 'error_msg': None}
        action_type = request.data['action_type'] if request.data['action_type'] else 1
        next_step_data = Workflow(request.data['uid'], request.data['code'],
                                  request.data['pid'], request.data['current_state_id'], action_type)
        res = self.judge_work_order_type(next_step_data.get_next_data(), request.data['id'])
        if res['status']:
            request.data['current_state_id'] = res['data'][0]['next_state']
            request.data['operator'] = res['data'][0]['operator'] if res['data'][0]['operator'] else request.data[
                'proposer']
            queryset_obj = self.get_queryset().filter(id=kwargs['pk']).first()
            serializer = self.get_serializer(instance=queryset_obj, data=request.data, many=False)
            if serializer.is_valid():
                serializer.update(instance=queryset_obj, validated_data=request.data)
                # 确认当前进程是待发布且发布类似是apply才能触发镜像打包流程
                if serializer.data['current_state_id'] == "待发布" and action_type == 1:
                    self.matches_images(serializer.data)
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
    def init_request(item):
        """
        初始化当前请求的数据，根据请求的数据补全工单数据信息
        根据工单类型走不同的工作流，申请后的工单自动进入下一状态
        :param item: request.data 创建工单时接收的request数据
        :return: 处理后的request数据
        """
        result = {'status': False, 'data': item, 'message': None, 'form_data': None}
        form_data = {'begin_status': None,
                     'after_status': None,
                     'begin_operator': item['proposer'],
                     'operator': item['proposer'],
                     'after_operator': None,
                     'order_id': None,
                     }
        # res = WorkType.objects.filter(code=result['data']['code'], is_delete=False).values('id').first()
        workflow_data = Workflow(item['uid'], result['data']['code'], result['data']['pid'], '')
        res_data = workflow_data.get_next_data()
        if res_data['status']:
            for i in res_data['data']:
                if i['action']['action_type'] == 1:
                    result['data']['current_state_id'] = i['next_state']
                    if 'operator' not in result['data']:
                        result['data']['operator'] = i['operator'] if i['operator'] else item['proposer']
                    result['status'] = True
                    # result['data']['typeList'] = ','.join(str(v) for v in result['data']['type'])
                    # result['data']['type'] = res['id']
                    form_data['after_operator'] = result['data']['operator']
                    form_data['after_status'] = i['next_state']
                    form_data['begin_status'] = i['begin_state']
                    result['form_data'] = form_data
        return result

    @staticmethod
    def order_whether_complete(data):
        """
        同项目下的工单是否有未完成的；
        :param data:申请工单的详细信息
        :return:True/False
        """
        process_id = WorkType.objects.filter(code='local').values('processId').first()['processId']
        status_list = Status.objects.filter(state_type__in=[1, 2], process_id=process_id).values('status').all()
        result = LocalOrder.objects.filter(pid=data['pid'], is_delete=False, current_state_id__in=status_list).exists()
        return result

    @staticmethod
    def judge_work_order_type(item, pid):
        """
        根据工单发布类型确定工单发布人员
        data: 工单信息列表
        pid： 工单id
        :return: 字典{}
        local_order_tag:
         (1, "定制化发布"), 项目经理发布
         (2, "标准化发布"), 运维人员发布
        """
        local_order = LocalOrder.objects.filter(id=pid).values('deployTags', 'pid_id').first()
        local_order_tag = local_order['deployTags']
        local_order_pid = local_order['pid_id']
        next_state = item['data'][0]['next_state']
        operator = item['data'][0]['operator']
        order_role_nickname = OrderRolePermission.objects.filter(pid=local_order_pid, work_type__code='local').values(
            'uid__nickname', 'role__name').all()
        manager_list = []
        ops_list = []
        for items in order_role_nickname:
            if items['role__name'] == '项目经理':
                manager_list.append(items['uid__nickname'])
            elif items['role__name'] == '运维人员':
                ops_list.append(items['uid__nickname'])
        if next_state == '待发布' and local_order_tag == 1 and manager_list:
            operator = ','.join(manager_list)
        elif next_state == '待发布' and local_order_tag == 2 and ops_list:
            operator = ','.join(ops_list)
        if operator:
            item['data'][0]['operator'] = operator
        return item

    @staticmethod
    def list_project(uid):
        """
        列出当前用户是项目经理的所有项目id
        列出当前用户是有权限的所有项目id
        :param :uid 当前用户ID
        :return:{}
        """
        result = {'manage_list': [], 'all_list': [], 'all_list_id': []}
        pid_list = OrderRolePermission.objects.filter(uid=uid, work_type__code='local', role__name='项目经理') \
            .values('pid').all()
        all_pid_list = OrderRolePermission.objects.filter(uid=uid, work_type__code='local') \
            .values('pid').all().distinct()
        for res in pid_list:
            result['manage_list'].append(res['pid'])
        for item in all_pid_list:
            pid_name = LocalProject.objects.filter(id=item['pid']).values('id', 'name').first()
            result['all_list'].append(pid_name)
            result['all_list_id'].append(item['pid'])
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

    @staticmethod
    def get_status_list(data):
        """
        查询工单的某个状态类型下所有状态，列表过滤使用。例如下：
        处理中（正常）：测试审批中，发布中等
        已关闭（关闭）：关闭工单
        :param data:
        :return:
        """
        process_id = WorkType.objects.filter(code='local').values('processId').first()['processId']
        result = Status.objects.filter(state_type=data, process_id=process_id).values('status').all()
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
        work_order = LocalOrderDataView()
        work_order.mail_format(data)
        LocalOrderData.objects.create(begin_status=data['form_data']['begin_status'],
                                      after_status=data['form_data']['after_status'],
                                      begin_operator=data['form_data']['begin_operator'],
                                      operator=data['form_data']['operator'],
                                      after_operator=data['form_data']['after_operator'],
                                      order_id_id=order_id,
                                      note=data['form_data']['begin_status'],
                                      desc=data['form_data']['begin_status'])

    @staticmethod
    def matches_images(data):
        """
        正则匹配出表述（describe字段）中的镜像地址。
        :param data:
        :return:
        """
        dockerImage = []
        image_matches = re.findall(r"([a-z\d.:/-]+:[a-zA-Z\d_-]+)", data['describe'])
        # 遍历每一个镜像地址
        for image_match in image_matches:
            # 从镜像地址中提取出镜像名称和版本号部分
            name_version_match = re.search(r"([a-zA-Z\d_-]+:[a-zA-Z\d_-]+)$", image_match)
            if name_version_match:
                dockerImage.append("{}.tar".format(name_version_match.group(0).replace(":", "_")))
        if dockerImage:
            uploadFile = Ufile(dockerImage, data['id'])
            threading.Thread(target=uploadFile.backupImage()).start()


class LocalOrderDataView(ListModelMixin, CreateModelMixin, UpdateModelMixin, GenericViewSet):
    queryset = LocalOrderData.objects.filter(is_delete=False)
    serializer_class = LocalOrderDataSerializer

    def create(self, request, *args, **kwargs):
        """
        添加发布工单日志数据
        接口URL：$HOST/localDeploy/LocalOrderData/  方法：POST
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
            self.mail_format(request.data)
        else:
            result['data_status'] = 40000
            result['status'] = status.HTTP_200_OK
            result['error_msg'] = serializer.errors

        return APIResponse(data_status=result['data_status'], data=result['data'], status=result['status'],
                           error_msg=result['error_msg'])

    def list(self, request, *args, **kwargs):
        """
        添加工作流状态
        接口URL：$HOST/localDeploy/LocalOrderData/  方法：get
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

    @staticmethod
    def mail_format(data):
        """
        数据整理好，然后以邮件形式发送
        :param data: 工单数据
        """
        result = {'content': data, 'to_mail': [], 'sub': None}
        res = LocalOrder.objects.filter(id=data['order_id'], is_delete=False).values('create_time', 'describe',
                                                                                     'synopsis', 'deployTags',
                                                                                     'operator', 'priority',
                                                                                     'pid__name').first()
        result['content']['create_time'] = res['create_time'].strftime('%Y-%m-%d %H:%M:%S')
        result['content']['describe'] = res['describe']
        result['content']['type'] = 'local'
        result['sub'] = res['synopsis']
        result['content']['sub'] = res['synopsis']
        result['content']['id'] = data['order_id']
        result['content']['work_code'] = '本地化发布'
        result['content']['project_name'] = res['pid__name']
        result['content']['priority'] = res['priority']
        if res['deployTags'] == 1:
            result['content']['deployTags'] = '定制化发布'
        else:
            result['content']['deployTags'] = '标准化发布'
        for item in res['operator'].split(','):
            result['to_mail'].append(
                User.objects.filter(nickname=item, is_delete=False).values('email').first()['email'])
        sm = SendMail.SendMail(result)
        sm.order_send_mail()
