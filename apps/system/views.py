import os
import time

from rest_framework import status
from rest_framework.mixins import CreateModelMixin, ListModelMixin, UpdateModelMixin, DestroyModelMixin
from rest_framework.viewsets import GenericViewSet
from utils.Response import APIResponse


class ImageItemsView(CreateModelMixin, ListModelMixin, UpdateModelMixin, DestroyModelMixin, GenericViewSet):
    """
    图集
    """
    authentication_classes = []

    def create(self, request, *args, **kwargs):
        """
        上传图片进图集
        接口URL：$HOST/system/image/  方法：POST
        """
        result = {'data_status': None, 'data': [], 'header': None, 'status': None, 'error_msg': None}
        file = request.FILES['file']
        file.name = self.random_file_name(file.name)
        with open('media/images/'+file.name, 'wb') as f:  # 将图片以二进制的形式写入
            for data in file.chunks():
                f.write(data)
                result['data'].append('media/images/'+file.name)
            result['data_status'] = 20000
            result['status'] = status.HTTP_200_OK
        return APIResponse(data_status=result['data_status'], data=result['data'], status=result['status'],
                           error_msg=result['error_msg'])

    @staticmethod
    def random_file_name(name):
        """
        重定义文件名称，时间戳+文件名后缀
        :param name: 文件名
        :return: 修改后的文件名
        """
        ext = os.path.splitext(name)[1]
        new_name = str(int(round(time.time() * 1000)))
        name = new_name + ext
        return name
