from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin, CreateModelMixin, RetrieveModelMixin, UpdateModelMixin, \
    DestroyModelMixin
from host.models import HostInfo, HostToProject
from deploy.models import Project
from system.workflow import OrderRolePermission
from host.serializer import HostInfoSerializer
from host.ucloud import UCloudApi
from utils import paginations
from rest_framework import status
from utils.Response import APIResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework_jwt.authentication import jwt_decode_handler


class HostInfoView(ListModelMixin, CreateModelMixin, UpdateModelMixin, DestroyModelMixin, GenericViewSet,
                   RetrieveModelMixin):
    queryset = HostInfo.objects.filter(is_delete=False)
    serializer_class = HostInfoSerializer
    pagination_class = paginations.PageNumberPagination
    filter_backends = (DjangoFilterBackend, SearchFilter)
    filter_fields = ('env',)
    search_fields = ('OSName', 'ip', 'name')

    def create(self, request, *args, **kwargs):
        """
        同步主机信息至数据库
        接口URL：$HOST/host/hostInfo/  方法：POST
        body：{
                'id': 'ID',
                'name': '主机名',
                'CPU': 'CPU',
                'memory': '内存',
                'OSName': '操作系统',
                'OSType': '系统类型',
                'ip': 'IP地址',
                'env' "环境"
                }
        """
        result = {'data_status': None, 'data': None, 'header': None, 'status': None, 'error_msg': None}
        if request.data:
            serializer = self.get_serializer(data=request.data)
        else:
            data = self.get_host_list()
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

    def list(self, request, *args, **kwargs):
        """
        查看主机信息
        接口URL：$HOST/host/hostInfo/  方法：get
        """
        jwt_value = request.META.get('HTTP_X_TOKEN')
        uid = jwt_decode_handler(jwt_value)['pk']
        projectList = self.list_project(uid)
        result = {'data_status': None, 'data': None, 'header': None, 'status': None, 'error_msg': None}

        title = \
            {
                'id': 'ID',
                'name': '主机名',
                'CPU': 'CPU',
                'memory': '内存',
                'OSName': '操作系统',
                'OSType': '系统类型',
                'ip': 'IP地址',
                'pName': '项目组'
            }
        if request.GET.get('ip'):
            self.queryset = self.queryset.filter(ip__contains=request.GET.get('ip'))
        if request.GET.get('project'):
            hostList = HostToProject.objects.filter(pid_id=request.GET.get('project')).values('hid')
            hostID = []
            for item in hostList:
                hostID.append(item['hid'])
            query_set = self.queryset.filter(id__in=hostID).all()
            queryset = self.filter_queryset(query_set).order_by('-create_time')
        elif self.is_not_supper(jwt_decode_handler(jwt_value)['role_name']):
            queryset = self.filter_queryset(self.get_queryset()).order_by('-create_time')
        else:
            query_set = self.queryset.filter(hosttoproject__pid__in=projectList['all_list_id']).all()
            queryset = self.filter_queryset(query_set).order_by('-create_time')
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
                           error_msg=result['error_msg'], title=title, total=total, projectList=projectList)

    def update(self, request, *args, **kwargs):
        """
        单个更新
        更新工作流名称信息
        接口URL：$HOST/host/hostInfo/{id}/  方法：put/patch
        body：{"name": "新测试"}
        """
        result = {'data_status': None, 'data': None, 'header': None, 'status': None, 'error_msg': None}
        queryset_obj = HostInfo.objects.filter(id=kwargs['pk']).first()
        serializer = self.get_serializer(instance=queryset_obj, data=request.data, many=False)
        if serializer.is_valid():
            serializer.update(instance=queryset_obj, validated_data=request.data)
            self.update_project_relevance(request.data['id'], request.data['pName'])
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
        删除该工作流名称
        接口URL：$HOST/host/hostInfo/{id}/  方法：delete
        """
        result = {'data_status': None, 'data': None, 'header': None, 'status': None, 'error_msg': None}
        res = HostInfo.objects.filter(id=kwargs['pk']).update(is_delete=True)
        if res:
            result['data_status'] = 20000
            result['status'] = status.HTTP_200_OK
        else:
            result['data_status'] = 40000
            result['status'] = status.HTTP_200_OK
            result['error_msg'] = "删除失败"
        return APIResponse(data_status=result['data_status'], data=result['data'], status=result['status'],
                           error_msg=result['error_msg'])

    def sync_host_info(self, signature, ProjectId, env):
        result = []
        publicKey = "k3IWzCZQQHy1/XIEf5AS411E7nJPnO5OXiYNHW0KAeFeFIH0"
        Region = "cn-bj2"
        res = UCloudApi(publicKey, signature, Region, ProjectId)
        data = res.get_host_info()
        if data['RetCode'] == 0:
            for item in data['UHostSet']:
                host_obj = dict()
                host_obj['name'] = item['Name']
                host_obj['CPU'] = item['CPU']
                host_obj['memory'] = item['Memory']
                host_obj['OSType'] = item['OsType']
                host_obj['OSName'] = item['OsName']
                host_obj['describe'] = item['Tag']
                host_obj['ip'] = item['IPSet'][0]['IP']
                host_obj['env'] = env  # (1, "预生产环境"), (2, "生产环境"), (3, "测试环境"),(4, "开发环境"),
                if not self.filtration_host_info(host_obj['ip']):
                    result.append(host_obj)
        return result

    def get_host_list(self):
        """
        获取所有环境下的主机信息
        :return:
        """

        '''生产环境主机信息列表'''
        signature_prod = "d86c69bd65352074dd33296f9ea5c32b3764caae"
        ProjectId_prod = "org-faogi1"
        result_prod = self.sync_host_info(signature_prod, ProjectId_prod, 2)

        '''预生产环境主机信息列表'''
        signature_pre = "b61a9f4acc3d12ab1908e0d79f6f5bd468eb8235"
        ProjectId_pre = "org-1dikq2"
        result_pre = self.sync_host_info(signature_pre, ProjectId_pre, 1)

        '''测试环境主机信息列表'''
        signature_test = "a9792bc43756391314e2db6393dda8ae0ce580a0"
        ProjectId_test = "org-33324"
        result_test = self.sync_host_info(signature_test, ProjectId_test, 3)

        result = result_prod+result_pre+result_test
        return result

    @staticmethod
    def filtration_host_info(ip):
        """
        判断主机列表中是否包含此ip
        :return: list
        """
        return HostInfo.objects.filter(ip=ip).exists()

    @staticmethod
    def update_project_relevance(hid, projectList):
        """
        修改主机关联的项目列表
        :param hid: 主机信息ID
        :param projectList: 主机关联的项目ID列表
        :return:
        """
        result = False
        if hid or projectList:
            HostToProject.objects.filter(hid=hid).delete()
            for item in projectList:
                HostToProject.objects.create(hid_id=hid, pid_id=item)
                result = True
        return result

    @staticmethod
    def list_project(uid):
        """
        列出当前用户是有权限的所有项目id
        :param :uid 当前用户ID
        :return:{}
        """
        result = {'manage_list': [], 'all_list': [], 'all_list_id': []}
        all_pid_list = OrderRolePermission.objects.filter(uid=uid, work_type__code='deploy') \
            .values('pid').all().distinct()
        for item in all_pid_list:
            pid_name = Project.objects.filter(id=item['pid']).values('id', 'name').first()
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
