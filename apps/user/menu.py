from django.http import HttpResponse
from user import models
import re


class MenuHelper(object):
    # 判断角色是否有权限访问URL的类
    def __init__(self, request, username):
        # 当前请求的request对象
        self.request = request
        # 当前用户名
        self.username = username
        # 获取当前URL
        self.current_url = request.path_info
        # 获取当前用户的所有权限
        self.permission2action_dict = None
        # 获取在菜单中显示的权限
        self.menu_leaf_list = None
        # 获取所有菜单
        self.menu_list = None
        self.menu_data()

    def menu_data(self):
        # 获取当前用户的角色列表
        role_list = models.Role.objects.filter(UserInfoRole__userID__username=self.username)
        # 查询当前用户的接口对应的操作权限
        permission2action_list = models.Interface_Action.objects.filter(
            Interface_Action_Role__r__in=role_list).values('p__url', 'a__code').distinct()
        permission2action_dict = {}
        for item in permission2action_list:
            if item['p__url'] in permission2action_dict:
                permission2action_dict[item['p__url']].append(item['a__code'])
            else:
                permission2action_dict[item['p__url']] = [item['a__code'], ]
        # 获取菜单的叶子节点，即：菜单的最后一层应该显示的权限
        menu_leaf_list = list(
            models.Interface_Action.objects.filter(Interface_Action_Role__r__in=role_list).exclude(
                p__menu__isnull=True).values('p_id', 'p__url', 'p__caption', 'p__menu').distinct())
        # 获取所有的菜单列表
        menu_list = list(models.Menu.objects.values('id', 'caption', 'parent_id'))
        self.menu_list = menu_list
        self.menu_leaf_list = menu_leaf_list
        self.permission2action_dict = permission2action_dict

    def menu_data_list(self):
        # 获取用户能访问的菜单树
        menu_leaf_dict = {}
        open_leaf_parent_id = None
        # 列出所有的叶子节点
        for item in self.menu_leaf_list:
            item = {'id': item['p_id'],
                    'url': item['p__url'],
                    'caption': item['p__caption'],
                    'parent_id': item['p__menu'],
                    'child': [],
                    'status': True,  # 是否显示
                    'open': False}
            if item['parent_id'] in menu_leaf_dict:
                menu_leaf_dict[item['parent_id']].append(item)
            else:
                menu_leaf_dict[item['parent_id']] = [item, ]
            # 如果URL是当前访问页面，item['open'] 设置为 True，用于菜单展开。
            if re.match("^" + item['url'], self.current_url):
                item['open'] = True
                open_leaf_parent_id = item['parent_id']
        # 获取所有菜单字典
        menu_dict = {}
        for item in self.menu_list:
            item['child'] = []
            item['status'] = False
            item['open'] = False
            menu_dict[item['id']] = item
        # 讲叶子节点添加到菜单中
        for k, v in menu_leaf_dict.items():
            menu_dict[k]['child'] = v
            parent_id = k
            # 将后代中有叶子节点的菜单标记为【显示】
            while parent_id:
                menu_dict[parent_id]['status'] = True
                parent_id = menu_dict[parent_id]['parent_id']
        # 将已经选中的菜单标记为【展开】
        while open_leaf_parent_id:
            menu_dict[open_leaf_parent_id]['open'] = True
            open_leaf_parent_id = menu_dict[open_leaf_parent_id]['parent_id']
        # 生成树形结构数据
        result = []
        for row in menu_dict.values():
            # 仅显示status为true的菜单
            if not row['status']:
                continue
            # 首页菜单不显示，在菜单导航页设定死了
            if row['caption'] == "Dashboard":
                continue
            # 如果菜单没有父菜单,则直接加入菜单目录
            elif not row['parent_id']:
                result.append(row)
            else:
                menu_dict[row['parent_id']]['child'].append(row)
        return result


