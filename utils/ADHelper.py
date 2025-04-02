from config import ldap as settings
from ldap3 import Connection, SUBTREE, Server
# from ldap3.core import exceptions
import datetime


class AD:

    def __init__(self):
        self.ldap_server_pool = Server(settings.LDAP_SERVER, port=settings.LDAP_SERVER_PORT, use_ssl=True)
        self.conn = Connection(self.ldap_server_pool, user=settings.ADMIN_DN, password=settings.ADMIN_PASSWORD,
                               check_names=True,
                               lazy=False,
                               raise_exceptions=False)
        self.conn.start_tls()

    def auth(self, username, password):
        self.conn.open()
        self.conn.bind()
        res = self.conn.search(
            search_base=settings.SEARCH_BASE,
            search_filter='(sAMAccountName={})'.format(username),
            search_scope=SUBTREE,
            attributes=['cn', 'mail', "sAMAccountName", "givenName", "userAccountControl"],
            paged_size=5
        )
        if res:

            try:
                entry = self.conn.response[0]
                dn = entry['dn']
                attr_dict = entry['attributes']
                conn2 = Connection(self.ldap_server_pool, user=dn, password=password, check_names=True, lazy=False,
                                   raise_exceptions=False)
                conn2.bind()
                if conn2.result["description"] == "success":
                    department = entry['dn'].split(',')[1].split('=')[1]
                    return True, attr_dict["mail"], attr_dict["sAMAccountName"], attr_dict["cn"], department
                else:
                    return False
            except Exception as e:
                return False
        else:
            return False

    def get_user(self):
        self.conn.open()
        self.conn.bind()
        self.conn.search(search_base='DC=isesol,DC=local',
                         search_filter='(&(objectclass=person)(!(sn=uri))(userAccountControl=66048))',
                         search_scope=SUBTREE,
                         attributes=['cn', 'mail', "sAMAccountName", "givenName", "pwdLastSet", "userAccountControl"],
                         )
        user_list = []
        for user in self.conn.response:
            if 'raw_dn' in user:
                if user['attributes']['userAccountControl'] == 66048:
                    pass_expr = datetime.datetime(month=12, year=2099, day=31)
                else:
                    pass_expr = user['attributes']['pwdLastSet'] + datetime.timedelta(days=90)

                user_list.append(
                    [user['attributes']['cn'], user['attributes']['sAMAccountName'], user['attributes']['mail'],
                     user['dn'].split(',')[1].split('=')[1], pass_expr])

        if user_list:
            return True, user_list
        else:
            return False, '获取数据失败'

    def set_password(self, username, password, old_password):
        self.conn.open()
        self.conn.bind()
        self.conn.search(search_base='DC=isesol,DC=local',
                         search_filter='(sAMAccountName={})'.format(username),
                         search_scope=SUBTREE,
                         )
        dn = self.conn.response[0]['dn']
        self.conn.extend.microsoft.modify_password(user=dn, new_password=password, old_password=old_password,
                                                   controls=None)
        if self.conn.result['description'] == 'success':
            return True
        else:
            return False
