from channels.generic.websocket import WebsocketConsumer
from django.http import QueryDict
from host.userDate import get_user_ssh_authority
from host.webSSH import WebSSH
import json
import logging
import time
logger = logging.getLogger('django')


class WebsocketSSH(WebsocketConsumer):
    message = {'status': 0, 'message': None}
    ssh = ''
    """
    status:
        0: ssh 连接正常, websocket 正常
        1: 发生未知错误, 关闭 ssh 和 websocket 连接

    message:
        status 为 1 时, message 为具体的错误信息
        status 为 0 时, message 为 ssh 返回的数据, 前端页面将获取 ssh 返回的数据并写入终端页面
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.wait_timeout = int(time.time())

    def connect(self):
        """
        打开 websocket 连接, 通过前端传入的参数尝试连接 ssh 主机
        :return:
        """
        self.accept()
        query_string = self.scope.get('query_string')
        ssh_args = QueryDict(query_string=query_string, encoding='utf-8')
        hid = ssh_args.get('id')
        uid = ssh_args.get('uid')
        HostSSHInfo = get_user_ssh_authority(hid, uid)
        width = 132
        height = 32
        port = 22
        passwd = HostSSHInfo['password']
        ip = HostSSHInfo['host']
        hUser = HostSSHInfo['user']
        ssh_key = HostSSHInfo['ssh_key']
        self.ssh = WebSSH(websocket=self, message=self.message)

        ssh_connect_dict = {
            'uid': uid,  # 用户ID
            'host': ip,  # 主机IP
            'user': hUser,  # 远程登入用户名
            'port': port,  # 远程端口
            'timeout': 60,
            'pty_width': width,  # 窗口宽
            'pty_height': height,  # 窗口高
            'password': passwd,  # 远程服务器密码
            'ssh_key': ssh_key   # 远程登入秘钥
        }
        self.ssh.connect(**ssh_connect_dict)

    # 断开会话连接
    def disconnect(self, close_code):
        try:
            if close_code == 3001:
                pass
            else:
                self.ssh.close()
        except Exception as e:
            logger.info('关闭SSH连接: %s' % e)
        finally:
            pass

    # 接受前端的信息传给主机
    def receive(self, text_data=None, bytes_data=None):
        if int(time.time()) - self.wait_timeout >= 900:
            logger.info('登录空闲超时!')
            self.ssh.close()
        if text_data is None:
            self.ssh.django_to_ssh(bytes_data)
        else:
            data = json.loads(text_data)
            if type(data) == dict:
                status = data['status']
                data = data['data']
                if status == 0:
                    self.wait_timeout = int(time.time())
                    self.ssh.shell(data)
                else:
                    cols = data['cols']
                    rows = data['rows']
                    self.ssh.resize_pty(cols=cols, rows=rows)
