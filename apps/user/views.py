from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin, CreateModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.exceptions import *
from .serializer import UserSerializer, PasswordSerializer, PermissionSerializer, RoleSerializer
from rest_framework_jwt.utils import jwt_decode_handler
from rest_framework import status
from utils.ADHelper import AD
from utils.JwtHelper import generate_token
from utils.Response import APIResponse
from .models import User, Role, Permission
from jwt import exceptions
from uuid import uuid4
from rest_framework.viewsets import ModelViewSet
from utils.JSONRenderer import JSONRenderer
from utils import paginations, ADHelper


class AuthView(CreateModelMixin, UpdateModelMixin, ListModelMixin, RetrieveModelMixin, GenericViewSet):
    """
    登入
    """
    queryset = User.objects.filter(is_delete=False)
    pagination_class = paginations.PageNumberPagination
    serializer_class = UserSerializer
    authentication_classes = []

    def create(self, request, *args, **kwargs):
        result = {'data_status': None, 'data': None, 'header': None, 'status': None, 'error_msg': None}
        data = dict()
        data['name'] = request.data.get('username')
        data['password'] = request.data.get('password')
        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            data = serializer.validated_data
            username = data['name']
            password = data['password']
            user = AD()
            user_detail = user.auth(username, password)
            if user_detail:
                user_obj = dict()
                user_obj['username'] = user_detail[2]
                user_obj['nickname'] = user_detail[3]
                user_obj['email'] = user_detail[1]
                user_obj['department'] = user_detail[4]
                # 判断用户是否存在
                user_get = User.objects.filter(username=user_obj['username'], is_delete=0).first()
                if user_get:
                    # 判断用户信息是否变更，如变更则更新数据
                    if user_obj['nickname'] != user_get.nickname or user_obj['email'] != user_get.email or \
                            user_obj['department'] != user_get.department:
                        User.objects.filter(username=user_obj['username']).update(nickname=user_obj['nickname'],
                                                                                  email=user_obj['email'],
                                                                                  department=user_obj['department'])
                else:
                    user_create = User.objects.create(**user_obj)
                    user_create.role.add(Role.objects.get(id=2))
                token = generate_token(user_obj['username'])

                result['data_status'] = 20000
                result['data'] = {'token': token}
                result['status'] = status.HTTP_200_OK
            else:
                result['data_status'] = 40000
                result['data'] = {}
                result['status'] = status.HTTP_200_OK
                result['error_msg'] = '用户名或密码错误'
        else:
            result['data_status'] = 40000
            result['data'] = {}
            result['status'] = status.HTTP_200_OK
            result['error_msg'] = serializer.errors

        return APIResponse(data_status=result['data_status'], data=result['data'], status=result['status'],
                           error_msg=result['error_msg'])

    def list(self, request, *args, **kwargs):
        """
        列出用户信息列表
        接口URL：$HOST/user/auth/  方法：get
        body：
        {
            "username": "用户名",
            "nickname": "昵称",
            "id":"用户id",
        }
        """
        result = {'data_status': None, 'data': None, 'header': None, 'status': None, 'error_msg': None}
        queryset = self.filter_queryset(self.get_queryset()).filter(
            nickname__contains=request.query_params['nickname']).order_by('-create_time').all()
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
                           error_msg=result['error_msg'], total=total)

    def retrieve(self, request, *args, **kwargs):
        """
        查询用户信息
        接口URL：$HOST/user/auth/id/  方法：OPTIONS
        body：
        {
            "username": "用户名",
            "nickname": "昵称",
            "id":"用户id",
        }
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

    def update(self, request, *args, **kwargs):
        """
        角色和用户关联表更新
        更新用户和角色的对应关系
        接口URL：$HOST/user/auth/id/ 方法：put/patch
        body：
        {
            "username": "用户名",
            "nickname":"昵称",
            "pk":"id",
        }
        """
        result = {'data_status': None, 'data': None, 'header': None, 'status': None, 'error_msg': None}
        # 更新所有用户的默认角色组
        if kwargs['pk'] == '0':
            if request.data['roleList']:
                # 新增用户与角色之间的默认关系
                for role in request.data['roleList']:
                    user = User.objects.all()
                    role = Role.objects.filter(name=role).first()
                    role.role.set(user)
            else:
                result['error_msg'] = '默认角色组不能为空！'
                result['data_status'] = 40000
                result['status'] = status.HTTP_200_OK
        # 更新所有用户的默认角色组
        elif kwargs['pk'] == '-1':
            if request.data['roleList']:
                # 新增用户与角色之间的默认关系
                for role in request.data['roleList']:
                    role = Role.objects.filter(name=role).first()
                    role.role.clear()
            else:
                result['error_msg'] = '默认角色组不能为空！'
                result['data_status'] = 40000
                result['status'] = status.HTTP_200_OK
        # 更新指定用户的角色组
        else:
            user = User.objects.filter(id=kwargs['pk']).first()
            # 清除原有用户与角色之间的关系
            user.role.clear()
            # 新增用户与角色之间的关系
            for role_name in request.data['role_name']:
                role = Role.objects.filter(name=role_name).first()
                # 新增用户与角色之间的关系
                user.role.add(role)
        return APIResponse(data_status=result['data_status'], data=result['data'], status=result['status'],
                           error_msg=result['error_msg'])

    def destroy(self, request, *args, **kwargs):
        """
        单个工单删除
        接口URL：$HOST/user/auth/id/  方法：delete
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


class InfoView(ListModelMixin, UpdateModelMixin, GenericViewSet):
    """
    :param: 通过jwt token解析
    通过username查询用户对应的role, 与token中的role做对比, 如果数据库中的role有更新，将重置用户的role并传给前端
    """

    def list(self, request, *args, **kwargs):
        result = {'data_status': None, 'data': None, 'header': None, 'status': None, 'error_msg': None}
        token = request.META.get('HTTP_X_TOKEN', None)
        if token:
            try:
                res = jwt_decode_handler(token)
                username = res['username']
                nickname = res['nickname']
                email = res['email']
                department = res['department']
                roles = res['role_name']
                avatar = res['avatar_url']
                uuid = res['uuid']

                role_query = User.objects.filter(username=username, uuid=uuid).values_list('role__name', 'id')
                uid = ''
                role_list = []
                if role_query:
                    uid = role_query[0][1]
                    for item in role_query:
                        role_list.append(item[0])

                if roles != role_list:
                    roles = role_list

                result['data_status'] = 20000
                result['data'] = {'roles': roles, 'name': username, 'avatar': avatar, 'nickname': nickname,
                                  'email': email, 'department': department, 'uid': uid}
                result['status'] = status.HTTP_200_OK
            except exceptions.DecodeError:
                raise AuthenticationFailed('token非法')

        else:
            result['data_status'] = 40000
        return APIResponse(data_status=result['data_status'], data=result['data'], error_msg=result['error_msg'])


class ADView(ListModelMixin, GenericViewSet):
    """
    :param: 手动同步AD账户信息
    """

    def list(self, request, *args, **kwargs):
        result = {'data_status': None, 'data': None, 'header': None, 'status': None, 'error_msg': None}
        user = ADHelper.AD()
        ad_status, user_list = user.get_user()
        if ad_status:
            for user in user_list:
                user_obj = dict()
                user_obj['username'] = user[1]
                user_obj['nickname'] = user[0]
                user_obj['email'] = user[2]
                user_obj['department'] = user[3]
                user_obj['account_expr'] = user[4]
                if not user_obj['email']:
                    continue
                # if not re.match('.*isesol.com', user[2]):
                #    continue
                obj = User.objects.filter(email=user[2]).first()
                if not obj:
                    User.objects.create(**user_obj)
                else:
                    obj.account_expr = user[4]
                    obj.save()
            result['error_msg'] = "同步成功！."
        else:
            result['error_msg'] = "获取用户信息失败."
        return APIResponse(data_status=result['data_status'], data=result['data'], error_msg=result['error_msg'])


class LogoutView(ListModelMixin, GenericViewSet):
    """
    :param: 通过jwt token解析
    通过username查询用户对应的uuid字段，每次logout时，都更新用户的uuid字段，配合全局的Authtication类，校验用户的token是否有效
    """

    def list(self, request, *args, **kwargs):
        result = {'data_status': None, 'data': None, 'header': None, 'status': None, 'error_msg': None}
        token = request.META.get('HTTP_X_TOKEN', None)
        # token = request.query_params.get('token', None)
        if token:
            try:
                res = jwt_decode_handler(token)
                name = res['username']
                user_obj = User.objects.filter(username=name)
                user_obj.update(uuid=uuid4())
            except exceptions.DecodeError:
                pass

        result['data_status'] = 20000
        result['status'] = status.HTTP_200_OK

        return APIResponse(data_status=result['data_status'], data=result['data'], error_msg=result['error_msg'])


class PasswordView(CreateModelMixin, GenericViewSet):
    serializer_class = PasswordSerializer
    authentication_classes = []

    def create(self, request, *args, **kwargs):
        result = {'data_status': None, 'data': None, 'header': None, 'status': None, 'error_msg': None}
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            old_password = serializer.validated_data['old_password']
            new_password = serializer.validated_data['new_password']
            user = AD()
            change_status = user.set_password(username, new_password, old_password)
            if change_status:
                result['data_status'] = 20000
            else:
                result['data_status'] = 40000
                result['error_msg'] = '修改密码失败'

        return APIResponse(data_status=result['data_status'], data=result['data'], error_msg=result['error_msg'])


class PermissionView(ListModelMixin, GenericViewSet):
    serializer_class = PermissionSerializer
    queryset = Permission.objects

    def list(self, request, *args, **kwargs):
        result = {'data_status': None, 'data': None, 'header': None, 'status': None, 'error_msg': None}
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        if serializer.is_valid:
            tree_dict = {}
            tree_data = []
            try:
                for item in serializer.data:
                    tree_dict[item['id']] = item

                for i in tree_dict:
                    if tree_dict[i]['pid']:
                        pid = tree_dict[i]['pid']
                        parent = tree_dict[pid]
                        parent.setdefault('children', []).append(tree_dict[i])
                    else:
                        tree_data.append(tree_dict[i])
                result['data'] = tree_data
            except KeyError:
                results = serializer.data
        return APIResponse(data_status=result['data_status'], data=result['data'], error_msg=result['error_msg'])


class RoleView(ModelViewSet):
    serializer_class = RoleSerializer
    queryset = Role.objects
    renderer_classes = [JSONRenderer, ]

    def create(self, request, *args, **kwargs):
        result = {'data_status': None, 'data': None, 'header': None, 'status': None, 'error_msg': None}
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        result['data_status'] = 20000
        result['data'] = serializer.data
        return APIResponse(data_status=result['data_status'], data=result['data'], error_msg=result['error_msg'])

    def list(self, request, *args, **kwargs):
        result = {'data_status': None, 'data': None, 'header': None, 'status': None, 'error_msg': None}
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        if serializer.is_valid:
            result['data'] = serializer.data
        return APIResponse(data_status=result['data_status'], data=result['data'], error_msg=result['error_msg'])

    def retrieve(self, request, *args, **kwargs):
        result = {'data_status': None, 'data': None, 'header': None, 'status': None, 'error_msg': None}
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        result['data'] = serializer.data
        return APIResponse(data_status=result['data_status'], data=result['data'], error_msg=result['error_msg'])

    def update(self, request, *args, **kwargs):
        result = {'data_status': None, 'data': None, 'header': None, 'status': None, 'error_msg': None}
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        result['data'] = serializer.data

        return APIResponse(data_status=result['data_status'], data=result['data'], error_msg=result['error_msg'])

    def destroy(self, request, *args, **kwargs):
        result = {'data_status': None, 'data': None, 'header': None, 'status': None, 'error_msg': None}
        instance = self.get_object()
        self.perform_destroy(instance)
        result['data_status'] = 20000
        return APIResponse(data_status=result['data_status'], data=result['data'], error_msg=result['error_msg'])
