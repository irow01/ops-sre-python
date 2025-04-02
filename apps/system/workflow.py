"""
Author:xwt
date:2019/12/12
介绍:工作流表，专门处理工单状态跳转。获取当前用户的权限及操作后的下一步状态信息！
"""
from system.models import WorkType, OrderRolePermission, Transition, Status, Action


class Workflow(object):
    """
    get_next_status方法点击操作触发：
        根据工单的操作信息，返回下一状态
    get_action_list页面刷新时触发：
        判断当前用户是否有操作权限
    """

    def __init__(self, uid, code, pid, status, action_type=1):
        # 工单当前状态
        self.status = status
        # 工单当前状态ID
        self.statusID = None
        # 工单当前的操作
        self.action_list = None
        # 当前操作的类型
        # (1, "批准"),
        # (2, "拒绝"),
        # (3, "取消"),
        # (4, "重新启动"),
        # (5, "解决"),
        self.action_type = action_type
        # 工单关联的pid
        self.pid = pid
        # 工单当前的操作用户id
        self.uid = uid
        # 工单当前的类型id
        self.work_type_id = None
        # 工单当前的类编号
        self.code = code
        # 工单关联的工作流
        self.processID = None
        self.initialization_data()

    def initialization_data(self):
        """
        获取类需要的基础数据
        :return:
        """
        res = WorkType.objects.filter(code=self.code, is_delete=False).values("id", "processId").first()
        self.processID = res['processId']
        self.work_type_id = res['id']
        if not self.status:
            self.status = Status.objects.filter(process_id=self.processID, state_type=1).values('status').first()[
                'status']

    def get_next_data(self):
        """
        获取下一步数据信息
        :return:样例如下：
        {
        'data': [{
                'next_state': '待测试审批',
                'operator': '熊文涛,魏旭升',
                'action':
                    {
                    'id': 8,
                    'values': '申请'
                    }
                }],
        'status': True,
        'message': None
        }
        """

        result = {'data': [], 'status': False, 'message': None}
        res = self.select_permission()
        # print("res:%s" % res)
        if res['status']:
            result['status'] = True
            for item in res['data']:
                arr = {'next_state': self.get_status_name(item['next_state_id']),
                       'operator': self.get_next_operator(item['next_state_id']),
                       'action': self.get_action(item['action_id']),
                       'begin_state': self.status
                       }
                result['data'].append(arr)
        else:
            result['message'] = '用户没有权限！'
        # print("result:%s" % result)
        return self.filter_data(result)

    def select_permission(self):
        """
        查询当前用户是否有操作权限
        :return: 当前用户有权限的操作及下一步状态
        {'data': [{'next_state_id': 1, 'action_id': 8, 'roles_list': '2,4,3'}], 'status': True}
        """
        result = {'data': [], 'status': False}
        roleList = []
        # 查询当前角色在该工单类型下的所有权限
        res = OrderRolePermission.objects.filter(uid=self.uid, work_type=self.work_type_id, pid=self.pid).values('role')
        for item in res:
            roleList.append(str(item['role']))
        # 查询当前工单下一步的操作，状态及有操作权限的角色组
        roles_list = Transition.objects.filter(process_id=self.processID,
                                               current_state_id=self.get_status_id(self.status),
                                               is_delete=False).values('next_state_id', 'action_id', 'roles_list')
        for items in roles_list:
            # 如果当前用户所在的角色有下一步操作的权限，则返回下一步的详细信息
            role_flag = list(set(roleList).intersection(set(items['roles_list'].split(','))))
            items['action_name'] = self.get_action(items['action_id'])
            proposer_flags = self.get_proposer_role(items['roles_list'])
            if role_flag or proposer_flags:
                result['status'] = True
                result['data'].append(items)
        return result

    def select_roles_username(self, roles_list):
        """
        根据角色列表及项目名称查询具体用户名称
        :param roles_list:字符串；角色列表
        :return: 下一步状态有权限操作的人员列表
        """
        username = []
        RolesList = []
        if roles_list.find(',') != -1:
            RolesList = roles_list.split(',')
        else:
            RolesList.append(roles_list)
        res = OrderRolePermission.objects.filter(pid=self.pid, work_type=self.work_type_id,
                                                 role__in=RolesList).values('uid__nickname')
        for item in res:
            username.append(item['uid__nickname'])
        return ','.join(set(username))

    def get_next_operator(self, next_state_id):
        """
        根据下一步状态获取下一步的经办人员
        :param next_state_id: 下一步的状态
        :return: 下一步的经办人员
        """
        transition_info = Transition.objects.filter(current_state_id=next_state_id, process_id=self.processID,
                                                    is_delete=False).values('roles_list', 'action_id')
        for item in transition_info:
            if self.get_action(item['action_id'])['action_type'] == self.action_type:
                return self.select_roles_username(item['roles_list'])

    def get_status_id(self, status):
        """
        根据状态ID获取状态名称
        :param status: 状态
        :return: 状态名称ID
        """
        return Status.objects.filter(process_id=self.processID, status=status, is_delete=False).values('id').first()['id']

    def get_status_name(self, status_id):
        """
        根据状态ID获取状态名称
        :param status_id: 状态id
        :return: 状态名称
        """
        return Status.objects.filter(process_id=self.processID, id=status_id, is_delete=False).values('status').first()[
            'status']

    def get_action(self, action_id):
        """
        根据状态ID获取状态名称
        :param action_id: 动作id
        :return: 状态名称,id及状态类型
        """
        return Action.objects.filter(process_id=self.processID, id=action_id, is_delete=False)\
            .values('id', 'status', 'action_type').first()

    def get_proposer_role(self, roles):
        """
        非发布工单，如果角色组权限包含有申请人角色，则跳过权限认证（返回True）
        :param roles: 返回的角色组id
        :return: True/False
        """
        # 角色组“申请人”的ID是14，默认非发布工单是任何人都可以申请的
        if roles == '14' and self.code != "deploy":
            return True
        else:
            return False

    def filter_data(self, data):
        """
        根据操作类型过滤数据
        :param data:
        {'data': [
            {'next_state': '待审批',
             'operator': '魏旭升,聂飞,熊文涛',
             'action':
                 {'id': 10,
                 'status': '校验通过',
                 'action_type': 1
                 },
             'begin_state': '待校验'},
            {'next_state': '申请',
             'operator': '魏旭升,聂飞,熊文涛',
             'action':
                 {'id': 16,
                 'status': '拒绝',
                 'action_type': 2
                 },
             'begin_state': '待校验'}
             ],
           'status': True,
            message': None}
        :return:
        """
        for item in data['data']:
            if not item['action']['action_type'] == self.action_type:
                data['data'].remove(item)
        return data
