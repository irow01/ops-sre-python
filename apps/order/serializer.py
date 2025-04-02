from rest_framework import serializers
from .models import OPSWorkOrder, OPSWorkOrderData
from system.models import Status, WorkType


class OPSWorkOrderSerializer(serializers.ModelSerializer):
    workType_name = serializers.ReadOnlyField(source='type.type')
    code = serializers.ReadOnlyField(source='type.code')
    priority_name = serializers.ChoiceField(choices=OPSWorkOrder.priority_list, source="get_priority_display",
                                            read_only=True)
    env = serializers.ChoiceField(choices=OPSWorkOrder.env, source="get_environment_display", read_only=True)
    state_type = serializers.SerializerMethodField(label='状态类型')

    class Meta:
        model = OPSWorkOrder
        fields = '__all__'
        read_only_fields = ['id', 'create_time', 'is_delete']

    @staticmethod
    def get_state_type(obj):
        """
        返回当前状态的类型
        固定写法,obj代表OPSWorkOrder实例对象
        """
        processId = WorkType.objects.filter(id=obj.type_id).values('processId').first()['processId']
        state_type = Status.objects.filter(process_id=processId, status=obj.current_state_id)\
            .values('state_type').first()
        return state_type['state_type']


class OPSWorkOrderDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = OPSWorkOrderData
        fields = '__all__'
        read_only_fields = ['id', 'create_time', 'is_delete']
