from rest_framework import serializers
from .models import Project, SubProject, WorkOrder, WorkOrderData
from system.models import Status


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'name', 'describe', 'shortName', 'is_load_balancing']
        read_only_fields = ['id', 'create_time', 'is_delete']


class SubProjectSerializer(serializers.ModelSerializer):
    environment = serializers.ChoiceField(choices=SubProject.environment, source="get_env_display", read_only=True)
    projectType = serializers.ChoiceField(choices=SubProject.projectType, source="get_type_display", read_only=True)
    pName = serializers.ReadOnlyField(source='project.name')
    pShortName = serializers.ReadOnlyField(source='project.shortName')
    jobs_name = serializers.SerializerMethodField(label='jobsName', read_only=True)

    class Meta:
        model = SubProject
        fields = '__all__'
        read_only_fields = ['id', 'create_time', 'is_delete']

    @staticmethod
    def get_jobs_name(obj):
        """
        返回jobsName
        固定写法,obj代表SubProject实例对象
        """
        environment = {1: "pre", 2: "prod", 3: "test", 4: "dev"}
        projectType = {1: "static", 2: "tomcat", 3: "python", 4: "go"}
        pShortName = Project.objects.filter(id=obj.project_id).values('shortName').first()
        myList = [environment[obj.env], pShortName['shortName'], projectType[obj.type], obj.name]
        return '-'.join(myList)

    def update(self, instance, validated_data):
        instance.ConfigCenter = validated_data['ConfigCenter']
        instance.PackageName = validated_data['PackageName']
        instance.ProjectName = validated_data['ProjectName']
        instance.ansible_group = validated_data['ansible_group']
        instance.command = validated_data['command']
        instance.domain = validated_data['domain']
        instance.env = validated_data['env']
        instance.git_address = validated_data['git_address']
        instance.interface_name = validated_data['interface_name']
        instance.label = validated_data['label']
        instance.name = validated_data['name']
        instance.type = validated_data['type']
        instance.webapp_dir = validated_data['webapp_dir']
        instance.save()
        return instance


class WorkOrderSerializer(serializers.ModelSerializer):
    state_type = serializers.SerializerMethodField(label='状态类型')
    project_name = serializers.ReadOnlyField(source='pid.name')
    priority_name = serializers.ChoiceField(choices=WorkOrder.priority_list, source="get_priority_display",
                                            read_only=True)
    env = serializers.ChoiceField(choices=WorkOrder.env, source="get_environment_display", read_only=True)

    class Meta:
        model = WorkOrder
        fields = '__all__'
        read_only_fields = ['id', 'create_time', 'is_delete']

    @staticmethod
    def get_state_type(obj):
        """
        返回当前状态的类型
        固定写法,obj代表WorkOrder实例对象
        """
        state_type = Status.objects.filter(process_id__worktype__code='deploy', status=obj.current_state_id)\
            .values('state_type').first()
        return state_type['state_type']

    def update(self, instance, validated_data):
        instance.operator = validated_data['operator']
        instance.current_state_id = validated_data['current_state_id']
        instance.save()
        return instance


class WorkOrderDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkOrderData
        fields = '__all__'
        read_only_fields = ['id', 'create_time', 'is_delete']