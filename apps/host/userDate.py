"""
Author : xiongwentao
Date   : 2020/10/26 下午2:34
Desc   : 获取用户数据及权限，专门用于webSocket接口
"""
from user.models import User
from host.models import HostInfo
# import logging
# logger = logging.getLogger('django')


def get_user_authority(uid):
    """
    判断用户是否为超级管理员
    :param uid: 用户ID
    :return: 布尔类型
    """
    result = False
    RoleList = User.objects.filter(id=uid).values('role__name').all()
    for item in RoleList:
        if 'supper' in item['role__name']:
            result = True
    return result


def get_user_ssh_authority(hid, uid):
    """

    :param hid: 主机ID
    :param uid: 用户ID
    :return:
    {'user': '',  # ssh用户
    'password': '', # ssh密码
    'host': ''  # 远程主机IP
    'ssh_key':''       # 密钥
    }
    """
    result = {'user': '', 'password': '', 'host': '', 'ssh_key': ''}
    is_supper = get_user_authority(uid)
    result['host'] = HostInfo.objects.filter(id=hid, is_delete=False).values('ip').first()['ip']
    if is_supper:
        result['user'] = 'isesol'
        result['password'] = 'j^nv)hwSMuDGnx)%'
    else:
        result['user'] = 'readonly'
        result['password'] = '$aXwj@b-HKyQ)dyK'
    return result


# def insert_host_access_log(host, user, cmd, uid):
#     try:
#         HostAccessLog.objects.create(ip=host, nid=uid, cmd=cmd, access_user=user)
#     except Exception as e:
#         logger.error('socket访问日志插入失败：error：　%s' % str(e))


