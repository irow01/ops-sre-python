import json
import os

from rest_framework.viewsets import GenericViewSet
from rest_framework import status
from rest_framework.mixins import ListModelMixin, CreateModelMixin, RetrieveModelMixin, UpdateModelMixin, \
    DestroyModelMixin
from django.conf import settings
from user.models import User
from order.models import OPSWorkOrder, OPSWorkOrderData
from system.models import WorkType, Status
from system.workflow import Workflow
from order.serializer import OPSWorkOrderSerializer, OPSWorkOrderDataSerializer
from utils import paginations, SendMail
from utils.Response import APIResponse
from django_filters.rest_framework import DjangoFilterBackend
from redis import StrictRedis, ConnectionPool
from rest_framework_jwt.authentication import jwt_decode_handler


class OPSWorkOrderView(ListModelMixin, CreateModelMixin, UpdateModelMixin, DestroyModelMixin, GenericViewSet,
                       RetrieveModelMixin):
    queryset = OPSWorkOrder.objects.filter(is_delete=False)
    serializer_class = OPSWorkOrderSerializer
    pagination_class = paginations.PageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('type',)

    def create(self, request, *args, **kwargs):
        """
        添加运维工单
        接口URL：$HOST/order/OPSWorkOrder/  方法：POST
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
        res = self.init_request(request.data)
        if res['status']:
            serializer = self.get_serializer(data=request.data)
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
            result['error_msg'] = res['message']

        return APIResponse(data_status=result['data_status'], data=result['data'], status=result['status'],
                           error_msg=result['error_msg'])

    def list(self, request, *args, **kwargs):
        """
        查询运维工单
        接口URL：$HOST/order/OPSWorkOrder/  方法：GET
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
        title = \
            {
                'synopsis': '概要',
                'proposer': '申请人',
                "operator": "经办人",
                "current_state_id": "状态",
                "environment": "环境",
                "create_time": "申请时间",
                "priority": "优先级",
                "type": "工单类型",
            }
        if request.GET.get('statusType'):
            status_list = self.get_status_list(request.GET.get('statusType'))
            query_set = OPSWorkOrder.objects.filter(is_delete=False, current_state_id__in=status_list).order_by(
                '-create_time')
        else:
            query_set = self.get_queryset()
        typeList = self.get_work_order_type()
        queryset = self.filter_queryset(query_set)
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
                           error_msg=result['error_msg'], title=title, total=total, typeList=typeList)

    def retrieve(self, request, *args, **kwargs):
        """
        查询运维工单
        接口URL：$HOST/order/OPSWorkOrder/id/  方法：OPTIONS
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
        jwt_value = request.META.get('HTTP_X_TOKEN')
        uid = jwt_decode_handler(jwt_value)['pk']
        result = {'data_status': None, 'data': None, 'header': None, 'status': None, 'error_msg': None}
        serializer = self.get_serializer(self.get_object())
        if serializer:
            result['data_status'] = 20000
            result['status'] = status.HTTP_200_OK
            result['data'] = serializer.data
            workflow = Workflow(uid, serializer.data['code'], 0, serializer.data['current_state_id'])
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
        接口URL：$HOST/order/OPSWorkOrder/id/  方法：delete
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
        接口URL：$HOST/order/OPSWorkOrder/id/ 方法：put/patch
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
                                  0, request.data['current_state_id'], action_type)
        res = next_step_data.get_next_data()
        if res['status']:
            request.data['current_state_id'] = res['data'][0]['next_state']
            request.data['operator'] = res['data'][0]['operator'] if res['data'][0]['operator'] else request.data[
                'proposer']
            queryset_obj = self.get_queryset().filter(id=kwargs['pk']).first()
            serializer = self.get_serializer(instance=queryset_obj, data=request.data, many=False)
            if serializer.is_valid():
                request.data.pop('type')
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
    def init_request(item):
        """
        初始化当前请求的数据，根据请求的数据补全工单数据信息
        根据工单类型走不同的工作流，申请后的工单自动进入下一状态
        :param item: request.data 创建工单时接收的request数据
        :return: 处理后的request数据
        """
        result = {'status': False, 'data': item, 'code': None, 'message': None, 'form_data': None}
        form_data = {'begin_status': None,
                     'after_status': None,
                     'begin_operator': item['proposer'],
                     'operator': item['proposer'],
                     'after_operator': None,
                     'order_id': None,
                     }
        res = WorkType.objects.filter(id=item['type'][0], is_delete=False).values('code').first()
        if res:
            result['code'] = res['code']
            workflow_data = Workflow(item['uid'], result['code'], 0, '')
            res_data = workflow_data.get_next_data()
            if res_data['status']:
                for i in res_data['data']:
                    if i['action']['action_type'] == 1:
                        result['data']['current_state_id'] = i['next_state']
                        if 'operator' not in result['data']:
                            result['data']['operator'] = i['operator'] if i['operator'] else item['proposer']
                        result['status'] = True
                        result['data']['typeList'] = ','.join(str(v) for v in result['data']['type'])
                        result['data']['type'] = item['type'][0]
                        form_data['after_operator'] = result['data']['operator']
                        form_data['after_status'] = i['next_state']
                        form_data['begin_status'] = i['begin_state']
                        result['form_data'] = form_data
        else:
            result['message'] = '工单申请失败！'
        return result

    @staticmethod
    def get_work_order_type():
        """
        获取工单类型列表（发布工单除外）
        :return: 字典{}
        """
        return WorkType.objects.exclude(code='deploy').filter(is_delete=False).values('id', 'type').all()

    @staticmethod
    def get_status_list(data):
        """
        查询工单的某个状态类型下所有状态，列表过滤使用。例如下：
        处理中（正常）：测试审批中，发布中等
        已关闭（关闭）：关闭工单
        (1, "开始"),
        (2, "正常"),
        (3, "完成"),
        (4, "拒绝"),
        (5, "已取消"),
        :param data:
        :return:
        """
        process_id = WorkType.objects.exclude(code='deploy').values('processId').all()
        result = Status.objects.filter(state_type__in=data.split(','), process_id__in=process_id).values('status').all()
        return result

    @staticmethod
    def insert_order_log(data, order_id):
        """
        申请操作记录写入数据库
        :param order_id: 工单ID
        :param data:
        {'data':{
            'form_data': {'begin_status': '申请',
                          'after_status': '审批',
                          'begin_operator': '熊文涛',
                          'operator': '熊文涛',
                          'after_operator': '魏旭升,熊文涛',
                          'order_id': None
                          }
            }
        }

        :return:工单日志的ID，判断日志是否插入数据库
        """
        data['form_data']['order_id'] = order_id
        data['form_data']['desc'] = data['form_data']['begin_status']
        ops_work_order = OPSWorkOrderDataView()
        ops_work_order.mail_format(data['form_data'])
        OPSWorkOrderData.objects.create(begin_status=data['form_data']['begin_status'],
                                        after_status=data['form_data']['after_status'],
                                        begin_operator=data['form_data']['begin_operator'],
                                        operator=data['form_data']['operator'],
                                        after_operator=data['form_data']['after_operator'],
                                        order_id_id=order_id,
                                        note=data['form_data']['begin_status'],
                                        desc=data['form_data']['begin_status'])


class WorkOrderInfoInRedis(CreateModelMixin, RetrieveModelMixin, GenericViewSet):
    """
    工单的附加信息存入redis，工单完成之后视事情插入数据库
    """
    pool = ConnectionPool(host=settings.REDIS_IP, port=6379, db=2, password=None)

    def create(self, request, *args, **kwargs):
        result = {'data_status': None, 'data': None, 'header': None, 'status': None, 'error_msg': None}
        redis = StrictRedis(connection_pool=self.pool)
        if len(request.data):
            redis.set(request.data['orderId'], request.data)
            result['data_status'] = 20000
            result['status'] = status.HTTP_200_OK
        else:
            result['data_status'] = 40000
            result['status'] = status.HTTP_200_OK
            result['error_msg'] = '上传数据至redis失败！'
        return APIResponse(data_status=result['data_status'], data=result['data'], status=result['status'],
                           error_msg=result['error_msg'])

    def retrieve(self, request, *args, **kwargs):
        result = {'data_status': None, 'data': None, 'header': None, 'status': None, 'error_msg': None}
        redis = StrictRedis(connection_pool=self.pool)
        if redis.exists(kwargs['pk']):
            result['data_status'] = 20000
            result['status'] = status.HTTP_200_OK
            result['data'] = eval(redis.get(kwargs['pk']).decode())
        else:
            result['data_status'] = 40000
            result['status'] = status.HTTP_200_OK
            result['error_msg'] = '无附件信息！'
        return APIResponse(data_status=result['data_status'], data=result['data'], status=result['status'],
                           error_msg=result['error_msg'])


class OPSWorkOrderDataView(ListModelMixin, CreateModelMixin, UpdateModelMixin, GenericViewSet):
    queryset = OPSWorkOrderData.objects.filter(is_delete=False)
    serializer_class = OPSWorkOrderDataSerializer

    def create(self, request, *args, **kwargs):
        """
        添加发布工单日志数据
        接口URL：$HOST/order/OPSWorkOrderData/  方法：POST
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
        接口URL：$HOST/order/OPSWorkOrderData/  方法：get
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
        res = OPSWorkOrder.objects.filter(id=data['order_id'], is_delete=False).values('create_time', 'describe',
                                                                                       'synopsis', 'type__code',
                                                                                       'operator', 'type__type').first()
        result['content']['create_time'] = res['create_time'].strftime('%Y-%m-%d %H:%M:%S')
        result['content']['describe'] = res['describe']
        result['content']['type'] = 'order'
        result['sub'] = res['synopsis']
        result['content']['sub'] = res['synopsis']
        result['content']['id'] = data['order_id']
        result['content']['work_code'] = res['type__code']
        result['content']['work_type'] = res['type__type']
        for item in res['operator'].split(','):
            result['to_mail'].append(
                User.objects.filter(nickname=item, is_delete=False).values('email').first()['email'])
        sm = SendMail.SendMail(result)
        sm.order_send_mail()
