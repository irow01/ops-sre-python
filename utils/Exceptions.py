from rest_framework.views import exception_handler
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
from rest_framework import status
from django.db import *
import logging

logger = logging.getLogger('django')


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        view = context['view']

        if isinstance(exc, DatabaseError):
            logging.error('[%s] %s' % (view, exc))
            response = Response({'message': '数据库内部错误'}, status=status.HTTP_507_INSUFFICIENT_STORAGE)
        if isinstance(exc, AuthenticationFailed):
            logging.error('[%s] %s' % (view, exc))
            response = Response({'message': '认证失败'}, status=status.HTTP_403_FORBIDDEN)
    return response
