from rest_framework import status
from rest_framework.mixins import CreateModelMixin, ListModelMixin, UpdateModelMixin, DestroyModelMixin
from rest_framework.viewsets import GenericViewSet
from system.models import Process, Status, Action, Transition, RoleGroup, Role, Group2Roles, WorkType
from system.serializer import ProcessSerializer, ProcessStatusSerializer, ProcessActionSerializer, \
    ProcessTransitionSerializer, RoleGroupSerializer, RolesSerializer, GroupInfoSerializer, WorkTypeSerializer
from utils.Response import APIResponse
from django_filters.rest_framework import DjangoFilterBackend


class WorkflowView(CreateModelMixin, ListModelMixin, UpdateModelMixin, DestroyModelMixin, GenericViewSet):
    """
    工作流
    """
    queryset = Process.objects.filter(is_delete=False)
    serializer_class = ProcessSerializer
    authentication_classes = []

    def create(self, request, *args, **kwargs):
        """
        添加工作流
        接口URL：$HOST/system/workflow/  方法：POST
        body：{"name": "测试"}
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
        查看工作流中的所有数据
        接口URL：$HOST/system/workflow/  方法：get
        """
        result = {'data_status': None, 'data': None, 'header': None, 'status': None, 'error_msg': None}
        title = \
            {
                'id': 'ID',
                'create_time': '创建时间',
                'state': '状态',
                'name': '工作流名称',
                'description': '描述',
                'role_group': '角色组'
            }
        queryset = self.filter_queryset(self.get_queryset())
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
                           error_msg=result['error_msg'], title=title)

    def update(self, request, *args, **kwargs):
        """
        单个更新
        更新工作流名称信息
        接口URL：$HOST/system/workflow/{id}/  方法：put/patch
        body：{"name": "新测试"}
        """
        result = {'data_status': None, 'data': None, 'header': None, 'status': None, 'error_msg': None}
        queryset_obj = Process.objects.filter(id=kwargs['pk']).first()
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
        删除该工作流名称
        接口URL：$HOST/system/workflow/{id}/  方法：delete
        """
        result = {'data_status': None, 'data': None, 'header': None, 'status': None, 'error_msg': None}
        res = Process.objects.filter(id=kwargs['pk']).update(is_delete=True)
        if res:
            result['data_status'] = 20000
            result['status'] = status.HTTP_200_OK
        else:
            result['data_status'] = 40000
            result['status'] = status.HTTP_200_OK
            result['error_msg'] = "删除失败"
        return APIResponse(data_status=result['data_status'], data=result['data'], status=result['status'],
                           error_msg=result['error_msg'])


class WorkflowStatusView(CreateModelMixin, ListModelMixin, UpdateModelMixin, DestroyModelMixin, GenericViewSet):
    """
    工作流状态
    工作流中的不同状态各有不同的属性类型（state_type）, 在此总结出几种常见的状态类型枚举:
    1、开始(start)：每个进程只应该一个。此状态是创建新请求时所处的状态。
    2、正常(normal)：没有特殊名称的常规状态。
    3、完成(complete)：表示此状态下的任何请求已正常完成的状态。
    4、拒绝(denied)：表示此状态下的任何请求已被拒绝的状态（例如，从未开始且不会被处理）。
    5、已取消(cancelled)：表示此状态下的任何请求已被取消的状态（例如，工作已开始但尚未完成）
    """
    queryset = Status.objects.filter(is_delete=False)
    serializer_class = ProcessStatusSerializer
    authentication_classes = []

    def create(self, request, *args, **kwargs):
        """
        添加工作流状态
        接口URL：$HOST/system/workflow/status/  方法：POST
        body：
        {
            "status": "申请,
            "state_type": "1",
            "description": "描述",
            "process_id": "2",

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
        接口URL：$HOST/system/workflow/status/  方法：get
        """
        result = {'data_status': None, 'data': None, 'header': None, 'status': None, 'error_msg': None}
        title = \
            {
                'id': 'ID',
                'create_time': '创建时间',
                'status': '状态',
                'state_type': '状态类型',
                'description': '描述',
                'process_id': '工作流'
            }
        queryset = self.filter_queryset(self.get_queryset()).filter(process_id=request.query_params['processId']).all()
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
                           error_msg=result['error_msg'], title=title)

    def update(self, request, *args, **kwargs):
        """
        单个更新
        更新工作流名称信息
        接口URL：$HOST/system/workflow/status/{id}/  方法：put/patch
        body：
        {
            "status": "申请,
            "state_type": "1",
            "description": "描述",
        }
        """
        result = {'data_status': None, 'data': None, 'header': None, 'status': None, 'error_msg': None}
        queryset_obj = Status.objects.filter(id=kwargs['pk']).first()
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
        接口URL：$HOST/system/workflow/status/{id}/  方法：delete
        """
        result = {'data_status': None, 'data': None, 'header': None, 'status': None, 'error_msg': None}
        res = Status.objects.filter(id=kwargs['pk']).update(is_delete=True)
        if res:
            result['data_status'] = 20000
            result['status'] = status.HTTP_200_OK
        else:
            result['data_status'] = 40000
            result['status'] = status.HTTP_200_OK
            result['error_msg'] = "删除失败"
        return APIResponse(data_status=result['data_status'], data=result['data'], status=result['status'],
                           error_msg=result['error_msg'])


class WorkflowActionView(CreateModelMixin, ListModelMixin, UpdateModelMixin, DestroyModelMixin, GenericViewSet):
    """
    工作流操作
    同样的不同的动作也各有不同的属性类型, 在此总结出几种常见的动作类型枚举:
    1、批准(approve)：操作人将请求应移至下一个状态。
    2、拒绝(deny)：操作人将请求应移至上一个状态。
    3、取消(cancel)：操作人将请求应在此过程中移至“已取消”状态。
    4、重新启动(restart)：操作人将将请求移回到进程中的“开始”状态。
    5、解决(resolve)：操作人将将请求一直移动到Completed状态。
    """
    queryset = Action.objects.filter(is_delete=False)
    serializer_class = ProcessActionSerializer
    authentication_classes = []

    def create(self, request, *args, **kwargs):
        """
        添加工作流状态
        接口URL：$HOST/system/workflow/action/  方法：POST
        body：
        {
            "status": "审批",
            "action_type": "1",
            "description": "描述",
            "process_id": "2",

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
        接口URL：$HOST/system/workflow/action/  方法：get
        """
        result = {'data_status': None, 'data': None, 'header': None, 'status': None, 'error_msg': None}
        title = \
            {
                'id': 'ID',
                'create_time': '创建时间',
                'status': '操作',
                'action_type': '操作类型',
                'description': '描述',
                'process_id': '工作流'
            }
        queryset = self.filter_queryset(self.get_queryset()).filter(process_id=request.query_params['processId'])
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
                           error_msg=result['error_msg'], title=title)

    def update(self, request, *args, **kwargs):
        """
        单个更新
        更新工作流名称信息
        接口URL：$HOST/system/workflow/action/{id}/  方法：put/patch
        body：
        {
            "status": "审批",
            "action_type": "1",
            "description": "描述",
        }
        """
        result = {'data_status': None, 'data': None, 'header': None, 'status': None, 'error_msg': None}
        queryset_obj = Action.objects.filter(id=kwargs['pk']).first()
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
        接口URL：$HOST/system/workflow/action/{id}/  方法：delete
        """
        result = {'data_status': None, 'data': None, 'header': None, 'status': None, 'error_msg': None}
        res = Action.objects.filter(id=kwargs['pk']).update(is_delete=True)
        if res:
            result['data_status'] = 20000
            result['status'] = status.HTTP_200_OK
        else:
            result['data_status'] = 40000
            result['status'] = status.HTTP_200_OK
            result['error_msg'] = "删除失败"
        return APIResponse(data_status=result['data_status'], data=result['data'], status=result['status'],
                           error_msg=result['error_msg'])


class WorkflowTransitionView(CreateModelMixin, ListModelMixin, UpdateModelMixin, DestroyModelMixin, GenericViewSet):
    """
    工作流转换，记录操作之后的状态变更
    """
    queryset = Transition.objects.filter(is_delete=False)
    serializer_class = ProcessTransitionSerializer
    authentication_classes = []

    def create(self, request, *args, **kwargs):
        """
        添加工作流状态
        接口URL：$HOST/system/workflow/transition/  方法：POST
        body：
        {
            "current_state_id": "1,
            "next_state_id": "2",
            "action_id": "2",
            "process_id": "2",
            "roles_list":""
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
        接口URL：$HOST/system/workflow/transition/  方法：get
        """
        result = {'data_status': None, 'data': None, 'header': None, 'status': None, 'error_msg': None}
        title = \
            {
                'id': 'ID',
                'create_time': '创建时间',
                'current_state_id': '当前状态',
                'next_state_id': '下一状态',
                'action_id': '操作',
                'process_id': '工作流',
                'roles_list': '角色列表'
            }
        relation_info = self.get_relation_info(request.query_params['processId'])
        queryset = self.filter_queryset(self.get_queryset()).filter(process_id=request.query_params['processId'])
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
                           error_msg=result['error_msg'], title=title, relation=relation_info)

    def update(self, request, *args, **kwargs):
        """
        单个更新
        更新工作流名称信息
        接口URL：$HOST/system/workflow/transition/{id}/  方法：put/patch
        body：
        {
            "current_state_id": "1,
            "next_state_id": "2",
            "action_id": "2",
            "roles_list":""
        }
        """
        result = {'data_status': None, 'data': None, 'header': None, 'status': None, 'error_msg': None}
        queryset_obj = Transition.objects.filter(id=kwargs['pk']).first()
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
        接口URL：$HOST/system/workflow/transition/{id}/  方法：delete
        """
        result = {'data_status': None, 'data': None, 'header': None, 'status': None, 'error_msg': None}
        res = Transition.objects.filter(id=kwargs['pk']).update(is_delete=True)
        if res:
            result['data_status'] = 20000
            result['status'] = status.HTTP_200_OK
        else:
            result['data_status'] = 40000
            result['status'] = status.HTTP_200_OK
            result['error_msg'] = "删除失败"
        return APIResponse(data_status=result['data_status'], data=result['data'], status=result['status'],
                           error_msg=result['error_msg'])

    @staticmethod
    def get_relation_info(pid):
        result = dict()
        res = Process.objects.filter(id=pid).values('role_group').all().first()
        if res:
            result['rolesList'] = Group2Roles.objects.filter(gid=res['role_group'], is_delete=False).values('rid',
                                                                                                            'rid__name')
        result['statusList'] = Status.objects.filter(process_id=pid, is_delete=False).values('id', 'status')
        result['actionList'] = Action.objects.filter(process_id=pid, is_delete=False).values('id', 'status')
        return result


class GroupView(CreateModelMixin, ListModelMixin, UpdateModelMixin, DestroyModelMixin, GenericViewSet):
    """
    工作流角色组
    """
    queryset = RoleGroup.objects.filter(is_delete=False)
    serializer_class = RoleGroupSerializer
    authentication_classes = []

    def create(self, request, *args, **kwargs):
        """
        添加角色组
        接口URL：$HOST/system/roles/  方法：POST
        body：
        {
            "name": "1,
            "description": "2",
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
        接口URL：$HOST/system/roles/  方法：get
        """
        result = {'data_status': None, 'data': None, 'header': None, 'status': None, 'error_msg': None}
        title = \
            {
                'id': 'ID',
                'create_time': '创建时间',
                'name': '角色组名称',
                'description': '描述',
            }
        queryset = self.filter_queryset(self.get_queryset())
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
                           error_msg=result['error_msg'], title=title)

    def update(self, request, *args, **kwargs):
        """
        单个更新
        更新工作流名称信息
        接口URL：$HOST/system/roles/{id}/  方法：put/patch
        body：
        {
            "name": "1,
            "description": "2",
        }
        """
        result = {'data_status': None, 'data': None, 'header': None, 'status': None, 'error_msg': None}
        queryset_obj = RoleGroup.objects.filter(id=kwargs['pk']).first()
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
        接口URL：$HOST/system/roles/{id}/  方法：delete
        """
        result = {'data_status': None, 'data': None, 'header': None, 'status': None, 'error_msg': None}
        res = RoleGroup.objects.filter(id=kwargs['pk']).update(is_delete=True)
        if res:
            result['data_status'] = 20000
            result['status'] = status.HTTP_200_OK
        else:
            result['data_status'] = 40000
            result['status'] = status.HTTP_200_OK
            result['error_msg'] = "删除失败"
        return APIResponse(data_status=result['data_status'], data=result['data'], status=result['status'],
                           error_msg=result['error_msg'])


class GroupInfoView(CreateModelMixin, ListModelMixin, UpdateModelMixin, DestroyModelMixin, GenericViewSet):
    """
    工作流角色组角色信息配置接口
    """
    queryset = Group2Roles.objects.filter(is_delete=False)
    serializer_class = GroupInfoSerializer
    authentication_classes = []

    def create(self, request, *args, **kwargs):
        """
        添加工作流状态
        接口URL：$HOST/system/groups/info/  方法：POST
        body：
        {
            "gid": "1",
            "rid": "1"
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
        接口URL：$HOST/system/groups/info/  方法：get
        """
        result = {'data_status': None, 'data': None, 'header': None, 'status': None, 'error_msg': None}
        title = \
            {
                'id': 'ID',
                'create_time': '创建时间',
                'rid': '角色名称',
            }

        queryset = self.filter_queryset(self.get_queryset()).filter(gid=request.query_params['group_id']).all()
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
                           error_msg=result['error_msg'], title=title)

    def update(self, request, *args, **kwargs):
        """
        单个更新
        更新工作流名称信息
        接口URL：$HOST/system/groups/info/{id}/  方法：put/patch
        body：
        {
            "gid": "1",
            "rid": "1",
        }
        """
        result = {'data_status': None, 'data': None, 'header': None, 'status': None, 'error_msg': None}
        queryset_obj = Group2Roles.objects.filter(id=kwargs['pk']).first()
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
        接口URL：$HOST/system/groups/info/{id}/  方法：delete
        """
        result = {'data_status': None, 'data': None, 'header': None, 'status': None, 'error_msg': None}
        res = Group2Roles.objects.filter(id=kwargs['pk']).update(is_delete=True)
        if res:
            result['data_status'] = 20000
            result['status'] = status.HTTP_200_OK
        else:
            result['data_status'] = 40000
            result['status'] = status.HTTP_200_OK
            result['error_msg'] = "删除失败"
        return APIResponse(data_status=result['data_status'], data=result['data'], status=result['status'],
                           error_msg=result['error_msg'])


class RolesView(CreateModelMixin, ListModelMixin, UpdateModelMixin, DestroyModelMixin, GenericViewSet):
    """
    工作流角色成员
    """
    queryset = Role.objects.filter(is_delete=False)
    serializer_class = RolesSerializer
    authentication_classes = []

    def create(self, request, *args, **kwargs):
        """
        添加工作流状态
        接口URL：$HOST/system/roles/  方法：POST
        body：
        {
            "name": "项目经理",
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
        接口URL：$HOST/system/roles/  方法：get
        """
        result = {'data_status': None, 'data': None, 'header': None, 'status': None, 'error_msg': None}
        title = \
            {
                'id': 'ID',
                'create_time': '创建时间',
                'name': '角色名称',
            }
        queryset = self.filter_queryset(self.get_queryset())
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
                           error_msg=result['error_msg'], title=title)

    def update(self, request, *args, **kwargs):
        """
        单个更新
        更新工作流名称信息
        接口URL：$HOST/system/roles/{id}/  方法：put/patch
        body：
        {
            "status": "申请,
            "state_type": "1",
            "description": "描述",
        }
        """
        result = {'data_status': None, 'data': None, 'header': None, 'status': None, 'error_msg': None}
        queryset_obj = Role.objects.filter(id=kwargs['pk']).first()
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
        接口URL：$HOST/system/roles/{id}/  方法：delete
        """
        result = {'data_status': None, 'data': None, 'header': None, 'status': None, 'error_msg': None}
        res = Role.objects.filter(id=kwargs['pk']).update(is_delete=True)
        if res:
            result['data_status'] = 20000
            result['status'] = status.HTTP_200_OK
        else:
            result['data_status'] = 40000
            result['status'] = status.HTTP_200_OK
            result['error_msg'] = "删除失败"
        return APIResponse(data_status=result['data_status'], data=result['data'], status=result['status'],
                           error_msg=result['error_msg'])


class WorkTypeView(ListModelMixin, UpdateModelMixin, GenericViewSet):
    """
    工单类型表，关联工作流
    """
    queryset = WorkType.objects.filter(is_delete=False)
    serializer_class = WorkTypeSerializer
    authentication_classes = []
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('code',)

    def list(self, request, *args, **kwargs):
        """
        查看资源
        接口URL：$HOST/system/workType/  方法：get
        """
        result = {'data_status': None, 'data': None, 'header': None, 'status': None, 'error_msg': None}
        title = \
            {
                'id': 'ID',
                "processId": "默认工作流",
                "code": "请求类型code",
                "type": "资源类型",
            }
        process_info = self.get_process_info()
        queryset = self.filter_queryset(self.get_queryset())
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
                           error_msg=result['error_msg'], title=title, process=process_info)

    def update(self, request, *args, **kwargs):
        """
        单个更新
        更新资源信息
        接口URL：$HOST/system/workType/{id}/  方法：put/patch
        body：
        {
            "processId": "默认工作流",
            "code": "请求类型code",
            "type": "资源类型",
        }
        """
        result = {'data_status': None, 'data': None, 'header': None, 'status': None, 'error_msg': None}
        queryset_obj = WorkType.objects.filter(id=kwargs['pk']).first()
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

    @staticmethod
    def get_process_info():
        result = dict()
        result['processList'] = Process.objects.filter(is_delete=False).values('id', 'name')
        return result


class StatusListView(ListModelMixin, GenericViewSet):
    """
    工单状态排序查询
    工作流中的不同状态各有不同的属性类型（state_type）, 在此总结出几种常见的状态类型枚举:
    1、开始(start)：每个进程只应该一个。此状态是创建新请求时所处的状态。
    2、正常(normal)：没有特殊名称的常规状态。
    3、完成(complete)：表示此状态下的任何请求已正常完成的状态。
    4、拒绝(denied)：表示此状态下的任何请求已被拒绝的状态（例如，从未开始且不会被处理）。
    5、已取消(cancelled)：表示此状态下的任何请求已被取消的状态（例如，工作已开始但尚未完成）
    """
    authentication_classes = []

    def list(self, request, *args, **kwargs):
        """
        查看资源
        接口URL：$HOST/system/workflow/statusList/  方法：get
        """
        result = {'data_status': None, 'data': None, 'header': None, 'status': None, 'error_msg': None}
        # statusList = []
        begin_status = ''
        # 查询工作流中的工作状态流转
        process_id = request.query_params['processId']
        transitionList = list(self.get_transition_list(process_id))
        # 排除工作流转中操作不是批准及完成的流转数据
        for item in transitionList:
            if not self.get_action_type(item['action_id'], process_id):
                transitionList.remove(item)
            else:
                if self.get_status_type(item['current_state_id'], process_id):
                    begin_status = item['current_state_id']
        statusList = self.order_status_list(transitionList, begin_status)
        statusNameList = self.get_status_name_list(statusList)
        if statusNameList is not None:
            result['data_status'] = 20000
            result['data'] = statusNameList
            result['status'] = status.HTTP_200_OK
        else:
            result['data_status'] = 20000
            result['status'] = status.HTTP_200_OK
            result['data'] = None
        return APIResponse(data_status=result['data_status'], data=result['data'], status=result['status'],
                           error_msg=result['error_msg'])

    @staticmethod
    def get_action_type(action_id, process_id):
        """
            获取工作流action的类型，返回状态是批准及完成action
            同样的不同的动作也各有不同的属性类型, 在此总结出几种常见的动作类型枚举:
            1、批准(approve)：操作人将请求应移至下一个状态。
            2、拒绝(deny)：操作人将请求应移至上一个状态。
            3、取消(cancel)：操作人将请求应在此过程中移至“已取消”状态。
            4、重新启动(restart)：操作人将将请求移回到进程中的“开始”状态。
            5、解决(resolve)：操作人将将请求一直移动到Completed状态。
        """
        return Action.objects.filter(id=action_id, process_id=process_id, is_delete=False, action_type__in=(1, 5))\
            .exists()

    @staticmethod
    def get_transition_list(process_id):
        """
        查询工作流中所有的工作流转信息
        :param process_id: 工作流ID
        :return: 字典，所有工作流转信息
        """
        TransitionList = Transition.objects.filter(is_delete=False, process_id=process_id)\
            .values('current_state_id', 'next_state_id', 'action_id').all()
        return TransitionList

    @staticmethod
    def get_status_type(status_id, process_id):
        """
        查询状态类型是开始的状态
        :param status_id: 状态ID
        :param process_id: 工作流ID
        :return: 布尔值（True/False）
        """
        return Status.objects.filter(id=status_id, process_id=process_id, is_delete=False, state_type=1)\
            .exists()

    @staticmethod
    def order_status_list(transition_list, begin_status):
        """
        状态排序
        :param transition_list:工作流中的工作流转数据
        :param begin_status: 开始状态ID
        :return: status_list列表，排序后的状态列表
        """
        status_list = [begin_status]
        current_state_id = begin_status
        for item in transition_list:
            if item['current_state_id'] == current_state_id:
                status_list.append(item['next_state_id'])
                current_state_id = item['next_state_id']
                continue
        return status_list

    @staticmethod
    def get_status_name_list(status_list):
        """
        把工作流状态id转换成工作流状态名称
        :param status_list: 工作流状态ID列表
        :return: 工作流状态名称列表
        """
        status_name_list = []
        for item in status_list:
            status_name = Status.objects.filter(id=item, is_delete=False).values('status').first()
            status_name_list.append(status_name.get('status'))
        return status_name_list
