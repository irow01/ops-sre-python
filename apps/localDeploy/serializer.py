from rest_framework import serializers
from .models import LocalProject, LocalOrder, LocalOrderData
from system.models import Status


class LocalProjectSerializer(serializers.ModelSerializer):
    projectType = serializers.ChoiceField(choices=LocalProject.tag, source="get_projectTags_display",
                                          read_only=True)

    class Meta:
        model = LocalProject
        fields = '__all__'
        read_only_fields = ['id', 'create_time', 'is_delete']


class LocalOrderSerializer(serializers.ModelSerializer):
    state_type = serializers.SerializerMethodField(label='状态类型')
    project_name = serializers.ReadOnlyField(source='pid.name')
    project_companyCode = serializers.ReadOnlyField(source='pid.companyCode')
    priority_name = serializers.ChoiceField(choices=LocalOrder.priority_list, source="get_priority_display",
                                            read_only=True)
    deployTags_name = serializers.ChoiceField(choices=LocalOrder.tag, source="get_deployTags_display", read_only=True)

    class Meta:
        model = LocalOrder
        fields = '__all__'
        # exclude = ['backup_mirror_url']  # 此字段流程中大部分为空，需要排除在序列化之外。否则会报“此字段不能为空的错误”
        read_only_fields = ['id', 'create_time', 'is_delete']

    @staticmethod
    def get_state_type(obj):
        """
        返回当前状态的类型
        固定写法,obj代表WorkOrder实例对象
        """
        state_type = Status.objects.filter(process_id__worktype__code='local', status=obj.current_state_id) \
            .values('state_type').first()
        return state_type['state_type']

    def update(self, instance, validated_data):
        instance.operator = validated_data['operator']
        instance.current_state_id = validated_data['current_state_id']
        instance.patch = f"iSIOT-{instance.id:08d}"
        instance.save()
        return instance


class LocalOrderDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = LocalOrderData
        fields = '__all__'
        read_only_fields = ['id', 'create_time', 'is_delete']
