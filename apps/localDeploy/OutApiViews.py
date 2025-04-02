from rest_framework.viewsets import GenericViewSet
from rest_framework import status
from rest_framework.mixins import ListModelMixin, UpdateModelMixin
from .serializer import LocalOrderSerializer
from .models import LocalOrder
from utils.Response import APIResponse
import hashlib
import json
import requests
import re


# LocalOrderInfoView 外部调用此接口，获取本地化工单的信息及本地化项目的所有信息返回给用户。 接口没有鉴权，使用自定义token鉴权
# 目前暂不使用
class LocalOrderInfoView(ListModelMixin, UpdateModelMixin, GenericViewSet):
    queryset = LocalOrder.objects.filter(is_delete=False)
    serializer_class = LocalOrderSerializer
    authentication_classes = []

    def list(self, request, *args, **kwargs):
        """
        接口URL：$HOST/localDeploy/iSIOT/  方法：get
        专门用于外部项目调用接口。独立的token认证
        :param request:
        :param args:
        :param kwargs: token patch
        :return:
        """
        result = {'data_status': None, 'data': None, 'header': None, 'status': None, 'error_msg': None}
        try:
            token = request.query_params['token']
            patch = request.query_params['patch']
            if self.token_check(token, patch):
                queryset = self.filter_queryset(self.get_queryset()).filter(patch=patch)
                serializer = self.get_serializer(queryset, many=True)
                if serializer.data[0]['current_state_id'] == "待发布":
                    result['data_status'] = 20000
                    result['status'] = status.HTTP_200_OK
                    result['data'] = self.get_company_info(serializer.data)
                else:
                    result['data_status'] = 40000
                    result['status'] = status.HTTP_200_OK
                    result['error_msg'] = "工单未审批或已关闭"
            else:
                result['data_status'] = 40000
                result['status'] = status.HTTP_200_OK
        except Exception as e:
            result['data_status'] = 40000
            result['status'] = status.HTTP_200_OK
            result['error_msg'] = e.args
        return APIResponse(data_status=result['data_status'], data=result['data'], status=result['status'],
                           error_msg=result['error_msg'])

    # 外部接口调用此方法关闭工单
    # 目前暂不使用
    def update(self, request, *args, **kwargs):
        """
        单个更新
        更新项目信息
        接口URL：$HOST/localDeploy/iSIOT/update/  方法：put/patch
        body：
        {
            "patch": "iSIOT-00000036",
            "token":"c5d9e4eb6050f1c5b57e156f7da3a051"
        }
        """
        result = {'data_status': None, 'data': None, 'header': None, 'status': None, 'error_msg': None}
        try:
            token = request.data['token']
            patch = request.data['patch']
            if self.token_check(token, patch):
                queryset_obj = LocalOrder.objects.filter(patch=patch)
                if queryset_obj.first().current_state_id == "待发布":
                    queryset_result = queryset_obj.update(current_state_id="完成", operator='system')
                    if queryset_result:
                        result['data_status'] = 20000
                        result['status'] = status.HTTP_200_OK
                    else:
                        result['data_status'] = 40000
                        result['status'] = status.HTTP_200_OK
                else:
                    result['data_status'] = 40000
                    result['status'] = status.HTTP_200_OK
                    result['error_msg'] = "工单未审批或已关闭"
        except Exception as e:
            result['data_status'] = 40000
            result['status'] = status.HTTP_200_OK
            result['error_msg'] = e.args
        return APIResponse(data_status=result['data_status'], data=result['data'], status=result['status'],
                           error_msg=result['error_msg'])

    @staticmethod
    def token_check(token, patch):
        """
        接口token认证
        :param token: 获取的token
        :param patch: 获取的工单编号
        :return: 是否认证通过
        """
        result = False
        if hashlib.md5((patch + 'isesol').encode('utf-8')).hexdigest() == token:
            result = True
        return result

    @staticmethod
    def get_company_info(item):
        """
        调用接口，获取本地化项目的服务器IP，账号及密码
        :param item: 字典
        :return: item 字典
        """
        url = 'https://api.isesol.com/gateway/basemanagerfront/oplocal/getOpLocalByCompanyCode'
        params = {'companyCode': item[0]['project_companyCode']}
        response = requests.post(url, params)
        # docker镜像地址正则匹配
        # pattern = r'[a-zA-Z0-9]+(?:\.[a-zA-Z0-9]+)*(?::\d+)?/[a-zA-Z0-9/_-]+:[\d]+'
        pattern = r'[a-zA-Z0-9]+(?:\.[a-zA-Z0-9]+)*(?::\d+)?/[a-zA-Z0-9/_-]+:([a-zA-Z0-9\-]+)'
        # 处理 API 响应
        if response.status_code == 200:
            # 获取 API 响应内容
            data = json.loads(response.text)
            # 处理数据
            for user in data:
                item[0]['companyCode'] = user['companyCode']
                item[0]['companyName'] = user['companyName']
                item[0]['serverIp'] = user['serverIp']
                item[0]['serverAccount'] = user['serverAccount']
                item[0]['serverPassword'] = user['serverPassword']
                item[0]['dockerImage'] = re.findall(pattern, item[0]['describe'])
        return item
