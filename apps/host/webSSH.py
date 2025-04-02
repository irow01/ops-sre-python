"""
Author : xiongwentao
Date   : 2020/9/3 下午2:34
Desc   : Terminal Socket 接口
"""
import paramiko
import json
from threading import Thread
import logging

# from host.userDate import insert_host_access_log

logger = logging.getLogger('django')


class WebSSH:
    def __init__(self, websocket, message):
        self.websocket = websocket
        self.message = message
        self.cmd = ''
        self.res = ''
        self.channel = ''
        # self.access_data = {}

    # term 可以使用 ansi, linux, vt100, xterm, dumb，除了 dumb外其他都有颜色显示
    def connect(self, uid, host, user, password=None, ssh_key=None, port=22, timeout=None,
                term='xterm', pty_width=80, pty_height=24):
        try:
            # 实例化SSHClient
            ssh_client = paramiko.SSHClient()
            # 当远程服务器没有本地主机的密钥时自动添加到本地，这样不用在建立连接的时候输入yes或no进行确认
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            # 用key进行认证
            if ssh_key:
                ssh_client.connect(username=user, hostname=host, port=port, pkey=ssh_key, timeout=timeout)
            else:
                # 用账号密码的方式进行认证
                ssh_client.connect(username=user, password=password, hostname=host, port=port, timeout=timeout)

            # 打开ssh通道，建立长连接.Transport是一种加密的会话
            transport = ssh_client.get_transport()
            self.channel = transport.open_session()
            # 获取ssh通道，并设置term和终端大小
            self.channel.get_pty(term=term, width=pty_width, height=pty_height)
            # 激活终端，正常登陆
            self.channel.invoke_shell()
            # 一开始展示Linux欢迎相关内容,后面不进入此方法
            logger.info('启动SSH连接,host: %s' % host)
            # self.access_data = {
            #     'host': host,
            #     'user': user,
            #     'cmd': self.cmd,
            #     'uid': uid
            # }
            for i in range(2):
                recv = self.channel.recv(1024).decode('utf-8')
                self.message['status'] = 0
                self.message['message'] = recv
                message = json.dumps(self.message)
                self.websocket.send(message)
                self.res += recv
        except Exception as e:
            self.message['status'] = 2
            self.message['message'] = 'connection failure...'
            logger.error('连接失败: %s' % str(e))
            message = json.dumps(self.message)
            self.websocket.send(message)
            self.websocket.close(3001)

    # 调整窗口大小
    def resize_pty(self, cols, rows):
        self.channel.resize_pty(width=cols, height=rows)

    # 向远程服务器发送命令
    def django_to_ssh(self, data):
        try:
            self.channel.send(data)
            if data == '\r':
                data = '\n'
            self.cmd += data
        except Exception as e:
            logger.error('连接失败: %s' % str(e))
            self.close()

    def websocket_to_django(self):
        try:
            while not self.channel.exit_status_ready():
                data = self.channel.recv(1024).decode('utf-8')
                if not len(data):
                    return
                self.message['status'] = 0
                self.message['message'] = data
                message = json.dumps(self.message)
                self.websocket.send(message)
        except Exception as e:
            logger.error('on_close error：　%s' % str(e))
            self.close()

    def close(self):
        try:
            # 关闭socket之前把操作命令录入数据库
            '''
            begin---收集操作日志并插入数据库，操作命令包含特殊字符等导致收集到的日志难以理解，故注释掉
            '''
            # self.cmd = "".join([s for s in self.cmd.splitlines(True) if s.strip()])
            # if self.cmd:
            #     self.access_data['cmd'] = self.cmd
            #     insert_host_access_log(**self.access_data)
            '''
            end 
            '''
            self.message['status'] = 1
            self.message['message'] = 'connection closed...'
            message = json.dumps(self.message)
            self.websocket.send(message)
            self.websocket.close()
            self.channel.close()
        except Exception as e:
            logger.error('连接关闭 error：　%s' % str(e))

    def shell(self, data):
        Thread(target=self.django_to_ssh, args=(data,)).start()
        Thread(target=self.websocket_to_django).start()
