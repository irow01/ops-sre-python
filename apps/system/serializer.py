from rest_framework import serializers
from .models import Process, Status, Action, Transition, RoleGroup, Role, Group2Roles, WorkType, OrderRolePermission


class ProcessSerializer(serializers.ModelSerializer):

    class Meta:
        model = Process
        fields = '__all__'
        read_only_fields = ['id', 'create_time']

    def save(self, **kwargs):
        Process.objects.create(**self.validated_data)

    def update(self, instance, validated_data):
        instance.name = validated_data['name']
        instance.state = validated_data['state']
        instance.description = validated_data['description']
        instance.role_group = validated_data['role_group']
        instance.save()
        return instance


class ProcessStatusSerializer(serializers.ModelSerializer):
    type = serializers.ChoiceField(choices=Action.type, source="get_state_type_display", read_only=True)

    class Meta:
        model = Status
        fields = '__all__'
        read_only_fields = ['id', 'create_time', 'process_id_id']

    def save(self, **kwargs):
        Status.objects.create(**self.validated_data)

    def update(self, instance, validated_data):
        instance.status = validated_data['status']
        instance.state_type = validated_data['state_type']
        instance.description = validated_data['description']
        instance.save()
        return instance


class ProcessActionSerializer(serializers.ModelSerializer):
    type = serializers.ChoiceField(choices=Action.type, source="get_action_type_display", read_only=True)

    class Meta:
        model = Action
        fields = '__all__'
        read_only_fields = ['id', 'create_time', 'process_id_id']

    def save(self, **kwargs):
        Action.objects.create(**self.validated_data)

    def update(self, instance, validated_data):
        instance.status = validated_data['status']
        instance.action_type = validated_data['action_type']
        instance.description = validated_data['description']
        instance.save()
        return instance


class ProcessTransitionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Transition
        fields = '__all__'
        read_only_fields = ['id', 'create_time', 'process_id_id']

    def save(self, **kwargs):
        Transition.objects.create(**self.validated_data)

    def update(self, instance, validated_data):
        instance.current_state_id = validated_data['current_state_id']
        instance.next_state_id = validated_data['next_state_id']
        instance.action_id = validated_data['action_id']
        instance.roles_list = validated_data['roles_list']
        instance.save()
        return instance


class RoleGroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = RoleGroup
        fields = '__all__'
        read_only_fields = ['id', 'create_time']

    def save(self, **kwargs):
        RoleGroup.objects.create(**self.validated_data)

    def update(self, instance, validated_data):
        instance.name = validated_data['name']
        instance.description = validated_data['description']
        instance.save()
        return instance


class RolesSerializer(serializers.ModelSerializer):

    class Meta:
        model = Role
        fields = '__all__'
        read_only_fields = ['id', 'create_time']

    def save(self, **kwargs):
        Role.objects.create(**self.validated_data)

    def update(self, instance, validated_data):
        instance.name = validated_data['name']
        instance.save()
        return instance


class GroupInfoSerializer(serializers.ModelSerializer):

    class Meta:
        model = Group2Roles
        fields = '__all__'
        read_only_fields = ['id', 'create_time']

    def save(self, **kwargs):
        Group2Roles.objects.create(**self.validated_data)

    def update(self, instance, validated_data):
        instance.rid_id = validated_data['rid']
        instance.gid_id = validated_data['gid']
        instance.save()
        return instance


class WorkTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = WorkType
        fields = '__all__'
        read_only_fields = ['id', 'create_time', 'code']

    def save(self, **kwargs):
        WorkType.objects.create(**self.validated_data)

    def update(self, instance, validated_data):
        instance.type = validated_data['type']
        instance.processId_id = validated_data['processId']
        instance.save()
        return instance


class PermissionSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(source='role.name')
    nickname = serializers.ReadOnlyField(source='uid.nickname')
    type = serializers.ReadOnlyField(source='work_type.type')

    class Meta:
        model = OrderRolePermission
        fields = ('id', 'pid', 'role', 'name', 'uid', 'nickname', 'work_type', 'type')
        read_only_fields = ['id']

    def save(self, **kwargs):
        OrderRolePermission.objects.create(**self.validated_data)

    def update(self, instance, validated_data):
        instance.role_id = validated_data['role']
        instance.uid_id = validated_data['uid']
        instance.save()
        return instance

