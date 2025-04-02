import jenkins
from django.conf import settings


# from API import models
# from ProjectReleased import models as p_models


class JenkinsTools(object):

    def __init__(self):
        self.server = jenkins.Jenkins(settings.JENKINS_URL, username=settings.JENKINS_USERNAME,
                                      password=settings.JENKINS_PASSWORD)

    def get_version(self):
        user = self.server.get_whoami()
        version = self.server.get_version()
        return 'Hello %s from Jenkins %s' % (user['fullName'], version)

    def get_job_count(self):
        number = self.server.jobs_count()
        return number

    def get_plugins_info(self):
        plugins_list = self.server.get_plugins()
        return plugins_list

    def get_job_info(self, name):
        info = self.server.get_job_info(name)
        return info

    def get_default_parameters(self, name):
        job_info = self.get_job_info(name)
        default_params = {}
        for action in job_info['actions']:
            if 'parameterDefinitions' in action:
                for param in action['parameterDefinitions']:
                    if 'defaultParameterValue' in param:
                        default_params[param['name']] = param['defaultParameterValue']['value']
        return default_params

    # def build_job(self, name, parameters):
    def build_job(self, name, parameters=None):
        # info = self.server.build_job(name, parameters, {'token':jenkins_token})
        # print('%s-------%s' %(name, parameters))
        if parameters is None:
            parameters = self.get_default_parameters(name)
        info = self.server.build_job(name, parameters)
        return info

    def get_queue_item(self, number, depth=0):
        info = self.server.get_queue_item(number, depth=0)
        return info

    def get_build_info(self, name, number):
        info = self.server.get_build_info(name, number)
        return info

    def get_build_status(self, name, number):
        info = self.server.get_build_info(name, number)
        return info['result']

    def get_running_builds(self):
        """
        get running build jobs for server.
        """
        info = self.server.get_running_builds()
        return info

    def get_build_console_output(self, name, number):
        try:
            info = self.server.get_build_console_output(name, number)
        except jenkins.JenkinsException:
            info = False
        return info

    def get_job_config(self, name):
        info = self.server.get_job_config(name)
        return info

    def get_last_completed_build_number(self, name):
        info = self.get_job_info(name)
        return info['lastSuccessfulBuild']['number']

    def get_last_unsuccessful_build_number(self, name):
        info = self.get_job_info(name)
        return info['lastUnsuccessfulBuild']['number']

    def get_all_jobs(self):
        info = self.server.get_all_jobs()
        item_list = []
        for item in info:
            if 'pre' in item['name']:
                item_list.append(item['name'])
            elif 'prod' in item['name']:
                item_list.append(item['name'])
        return item_list

# def build_jenkins_job(gid, namelist, env, rollback=False):
#     try:
#         JK = JenkinsTools()
#         if len(namelist) == 0:
#             return False, 'List Is None'
#         count_number = len(namelist)
#         build_number = {}
#         parameters = {"gid": gid, "countnumber": count_number, "env": env}
#         if rollback:
#             build_number = get_rollback_number(gid)
#         for name in namelist:
#             if rollback:
#                 parameters['Rollback_ID'] = int(build_number[name])
#             else:
#                 # 获取jenkins项目最后一次成功发布的buildID
#                 last_success_number = JK.get_last_completed_build_number(name)
#                 res = models.JenkinsRollback.objects.filter(jobname=name)
#                 if not res:
#                     models.JenkinsRollback.objects.create(jobname=name, build_number=last_success_number)
#                 else:
#                     res.update(build_number=last_success_number)
#             JK.build_job(name, parameters)
#
#         return True, ''
#     except Exception as e:
#         print(e)
#         return False, 'TypeError.'


# def get_rollback_number(order_id):
#     """
#     根据工单ID获取当前工单所有jobs的最后一次发布成功的版本号。
#     :param order_id: (工单id)
#     :return: result（字典）
#     """
#     result = {}
#     res = p_models.WorkOrder.objects.filter(id=order_id).values('released_list').first()
#     released_list = res['released_list'].split(",")
#     for item in released_list:
#         build_number = models.JenkinsRollback.objects.filter(jobname=item).values('build_number').first()
#         if build_number:
#             result[item] = build_number['build_number']
#         else:
#             result[item] = 0
#     return result
