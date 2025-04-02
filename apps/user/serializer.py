from rest_framework import serializers
from .models import User, Permission, Role


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=32, min_length=8, write_only=True)
    name = serializers.CharField(max_length=32, write_only=True)

    # role = serializers.PrimaryKeyRelatedField(queryset=Role.objects.all(), many=True)

    class Meta:
        model = User
        fields = ['name', 'pk', 'username', 'password', 'nickname', 'email', 'department', 'role_name',
                  'uuid', 'avatar_url']
        extra_kwargs = {
            'name': {
                # 'min_length': 3,
                'max_length': 32,
                'error_messages': {
                    'min_length': '用户名太短',
                    'max_length': '用户名太长',
                }
            },
            'username': {
                'read_only': True,
                'min_length': 3,
            },
            'password': {
                'write_only': True,
                'min_length': 3,
                'max_length': 32,
                'required': True,
                'error_messages': {
                    'required': '密码不能为空',
                    'min_length': '密码太短',
                    'max_length': '密码太长',
                }
            },
            'nickname': {
                'read_only': True,
            },
            'email': {
                'read_only': True,
            },
            'department': {
                'read_only': True,
            },
            'avatar': {
                'read_only': True,
            },
            'uuid': {
                'read_only': True,
            },
        }

    # def update(self, instance, validated_data):
    #     print(validated_data['role'])
    #     instance.role_name = validated_data['role']
    #     instance.save()
    #     return instance


class PasswordSerializer(serializers.Serializer):
    username = serializers.CharField(write_only=True, required=True)
    old_password = serializers.CharField(write_only=True, required=True, min_length=8)
    new_password = serializers.CharField(write_only=True, required=True, min_length=8)


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ['id', 'name', 'url', 'method', 'pid']


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'name', 'desc', 'description', 'permission']
        extra_kwargs = {
            'name': {
                # 'write_only': True,
                'min_length': 2,
                'max_length': 32,
                'error_messages': {
                    'required': '角色名称不能为空',
                    'min_length': '角色名称太短',
                    'max_length': '角色名称太长',
                }
            },
            'desc': {
                # 'write_only': True,
                'min_length': 2,
                'max_length': 32,
                'error_messages': {
                    'required': '描述不能为空',
                    'min_length': '描述太短',
                    'max_length': '描述太长',
                }
            }
        }
