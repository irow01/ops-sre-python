from rest_framework import serializers
from .models import HostInfo, HostToProject


class HostInfoSerializer(serializers.ModelSerializer):
    environment = serializers.ChoiceField(choices=HostInfo.environment, source="get_env_display", read_only=True)
    pName = serializers.SerializerMethodField(label='项目名称')

    class Meta:
        model = HostInfo
        fields = '__all__'
        read_only_fields = ['id', 'create_time', 'is_delete']

    @staticmethod
    def get_pName(obj):
        """
        返回项目名称
        固定写法,obj代表HostInfo实例对象
        """
        project = HostToProject.objects.filter(hid=obj.id).values('pid__name').all()
        projectList = []
        for item in project:
            projectList.append(item['pid__name'])
        if not projectList:
            projectList.append('未指定项目')
        return ','.join(projectList)
