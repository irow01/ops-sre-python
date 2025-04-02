from rest_framework import status
from rest_framework.mixins import CreateModelMixin, ListModelMixin, UpdateModelMixin, DestroyModelMixin
from rest_framework.viewsets import GenericViewSet
from utils.Response import APIResponse
from system.models import OrderRolePermission, WorkType, Role
from user.models import User
from deploy.models import Project
from system.serializer import PermissionSerializer
from django_filters.rest_framework import DjangoFilterBackend
from utils import paginations


class PermissionView(CreateModelMixin, ListModelMixin, UpdateModelMixin, DestroyModelMixin, GenericViewSet):
    """
    工作流角色成员
    """
    queryset = OrderRolePermission.objects
    serializer_class = PermissionSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('pid', 'work_type', 'uid')

    def create(self, request, *args, **kwargs):
        """
        添加工作流状态
        接口URL：$HOST/system/permission/  方法：POST
        body：
        {
            "pid": "1",
            "role": "2",
            "uid":"3",
            "work_type":"4",
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

    def list(self, request, *args, **kwargs):
        """
        查看工作流中的所有状态数据
        接口URL：$HOST/system/permission/  方法：get
        body：
        {
            "pid": "1",
            "work_type":"4",
            "uid":2
        }
        """
        result = {'data_status': None, 'data': None, 'header': None, 'status': None, 'error_msg': None}
        title = \
            {
                'id': 'ID',
                'role': '角色名称',
                'uid': '用户名',
                'work_type': '工单类型'
            }
        dataList = self.get_work_type(request.query_params['code'])
        # 当项目ID（pid）不为空
        if request.query_params['pid']:
            queryset = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(queryset)
            # 判断是否分页
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                result['data_status'] = 20000
                result['data'] = serializer.data
                result['status'] = status.HTTP_200_OK
            else:
                serializer = self.get_serializer(queryset, many=True)
                if serializer.is_valid:
                    result['data_status'] = 20000
                    result['status'] = status.HTTP_200_OK
                    result['data'] = serializer.data
                else:
                    result['data_status'] = 40000
                    result['status'] = status.HTTP_200_OK
                    result['error_msg'] = serializer.errors
        # 当项目ID（pid）为空
        else:
            result['data_status'] = 40000
            result['status'] = status.HTTP_200_OK
            result['error_msg'] = '您无任何项目查看权限！请联系对应项目的项目经理添加权限！'
        return APIResponse(data_status=result['data_status'], data=result['data'], status=result['status'],
                           error_msg=result['error_msg'], title=title, dataList=dataList)

    def update(self, request, *args, **kwargs):
        """
        单个更新
        更新工作流名称信息
        接口URL：$HOST/system/permission/{id}/  方法：put/patch
        body：
        {
            "status": "申请,
            "state_type": "1",
            "description": "描述",
        }
        """
        result = {'data_status': None, 'data': None, 'header': None, 'status': None, 'error_msg': None}
        queryset_obj = OrderRolePermission.objects.filter(id=kwargs['pk']).first()
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

    def destroy(self, request, *args, **kwargs):
        """
        单个删除
        删除该工作流状态
        接口URL：$HOST/system/permission/{id}/  方法：delete
        """
        result = {'data_status': None, 'data': None, 'header': None, 'status': None, 'error_msg': None}
        # instance = self.get_object().filter(id=kwargs['pk'])
        instance = self.get_object()
        self.perform_destroy(instance)
        if instance:
            result['data_status'] = 20000
            result['status'] = status.HTTP_200_OK
        else:
            result['data_status'] = 40000
            result['status'] = status.HTTP_200_OK
            result['error_msg'] = "删除失败"
        return APIResponse(data_status=result['data_status'], data=result['data'], status=result['status'],
                           error_msg=result['error_msg'])

    @staticmethod
    def get_work_type(code):
        result = dict()
        result['workType'] = WorkType.objects.filter(code=code, is_delete=False).values('id', 'processId__role_group') \
            .all().first()
        result['UserList'] = User.objects.values('id', 'nickname')
        result['RoleList'] = Role.objects.filter(group2roles__gid=result['workType']['processId__role_group'],
                                                 is_delete=False).values('id', 'name').distinct()
        return result


class PermissionUserView(CreateModelMixin, ListModelMixin, UpdateModelMixin, DestroyModelMixin, GenericViewSet):
    """
    工作流角色成员
    """
    queryset = OrderRolePermission.objects
    pagination_class = paginations.PageNumberPagination
    serializer_class = PermissionSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('uid',)

    def list(self, request, *args, **kwargs):
        """
        查看工作流中的所有状态数据
        接口URL：$HOST/system/permissionUser/  方法：get
        body：
        {
            "page_size": "1",
            "page":"4",
            "uid":2
        }
        """
        result = {'data_status': None, 'data': None, 'header': None, 'status': None, 'error_msg': None}
        title = \
            {
                'id': 'ID',
                'pname': '项目名称',
                'role': '角色名称',
                'uid': '用户名',
                'work_type': '工单类型'
            }
        dataList = self.get_work_type()
        uid = request.query_params['uid']
        if uid:
            queryset = self.filter_queryset(self.get_queryset()).filter(uid_id=uid)
        else:
            queryset = self.filter_queryset(self.get_queryset())
        total = queryset.count()
        page = self.paginate_queryset(queryset)
        # 判断是否分页
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            result['data_status'] = 20000
            result['data'] = serializer.data
            result['status'] = status.HTTP_200_OK
        else:
            serializer = self.get_serializer(queryset, many=True)
            if serializer.is_valid:
                result['data_status'] = 20000
                result['status'] = status.HTTP_200_OK
                result['data'] = serializer.data
            else:
                result['data_status'] = 40000
                result['status'] = status.HTTP_200_OK
                result['error_msg'] = serializer.errors
        result['data'] = self.get_pname(result['data'])
        return APIResponse(data_status=result['data_status'], data=result['data'], status=result['status'],
                           error_msg=result['error_msg'], total=total, title=title, dataList=dataList)

    @staticmethod
    def get_pname(code):
        """
        项目成员管理，通过项目id获取项目名称
        :param code:
        :return:
        """
        for item in code:
            if item['pid'] == 0:
                item['pname'] = '运维工单项目'
            else:
                item['pname'] = Project.objects.filter(id=item['pid']).values_list('name', flat=True).first()
        return code

    @staticmethod
    def get_work_type():
        result = dict()
        result['workType'] = WorkType.objects.filter(is_delete=False).values('id', 'processId__role_group') \
            .all().first()
        userList = []
        for item in OrderRolePermission.objects.values('uid_id', 'uid__nickname').distinct():
            user = {'id': item['uid_id'], 'nickname': item['uid__nickname']}
            userList.append(user)
        result['UserList'] = userList
        result['RoleList'] = Role.objects.filter(group2roles__gid=result['workType']['processId__role_group'],
                                                 is_delete=False).values('id', 'name').distinct()
        return result
