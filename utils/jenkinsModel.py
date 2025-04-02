"""
Author:xwt
date:2024/7/5
介绍:使用jenkinsApi插件实现jenkins接口调用
"""
from jenkinsapi.jenkins import Jenkins
from django.conf import settings
from jenkinsapi.custom_exceptions import JenkinsAPIException
import time


class JenkinsModel(object):

    def __init__(self):
        self.server = Jenkins(settings.JENKINS_URL, username=settings.JENKINS_USERNAME,
                              password=settings.JENKINS_PASSWORD, )

    def get_version(self):
        """
        获取jenkins调用用户及版本
        """
        user = self.server.username
        version = self.get_version()
        return 'Hello %s from Jenkins %s' % (user['fullName'], version)

    def get_build_console_output(self, name):
        """
        获取指定job的控制台输出
        """
        try:
            job = self.server.get_job(name)
            last_build = job.get_last_build()
            info = last_build.get_console()
        except JenkinsAPIException as e:
            # 捕获特定的 JenkinsAPIException 异常
            print(f"Error retrieving console output for job '{name}': {str(e)}")
            info = None  # 返回 None 或其他默认值
        except Exception as e:
            # 捕获其他未预料到的异常
            print(f"Unexpected error retrieving console output: {str(e)}")
            info = None  # 返回 None 或其他默认值
        return info

    def get_last_completed_build_number(self, name):
        """
        获取指定job的最后一次构建号
        """
        try:
            # 获取指定 job
            job = self.server.get_job(name)
            # 获取最后一次成功的构建
            last_successful_build = job.get_last_good_build()
            print("last_successful_build的值：", last_successful_build)
            if last_successful_build:
                return last_successful_build.get_number()
            else:
                return None  # 如果没有成功构建，返回 None
        except Exception as e:
            print(f"Failed to retrieve last successful build number for job '{name}': {str(e)}")
            return None

    def build_job(self, name):
        """
        构建job
        """
        if name in self.server.get_jobs_list():
            job = self.server.get_job(name)
            job.invoke()
            build = None
            while build is None:
                try:
                    build = job.get_last_build()
                except Exception as e:
                    print(f"Error while getting last build for job '{name}': {str(e)}")
                    time.sleep(1)
            return build.get_number()  # 返回构建号
        else:
            # 构建job不存在·
            return None

    def get_queue_item(self, name):
        try:
            queue = self.server.get_job(name)
            return queue.is_queued_or_running()
        except Exception as e:
            print(f"Failed to retrieve queue item for job '{name}': {str(e)}")
            return False

    def get_build_status(self, name, number):
        try:
            # 获取指定 job 的构建
            job = self.server.get_job(name)
            build = job.get_build(number)
            # 检查构建对象是否存在
            if build:
                # 返回构建的状态
                return build.get_status()
            else:
                print(f"Build #{number} for job '{name}' does not exist")
                return None
        except JenkinsAPIException as e:
            print(f"Jenkins API exception occurred: {str(e)}")
            return None
        except Exception as e:
            print(f"Failed to retrieve build status for job '{name}' build #{number}: {str(e)}")
            return None

    def get_last_buildnumber(self, job_name):
        """
        获取指定作业的最后一个构建编号。
        :param job_name: Jenkins作业名称
        :return: 最后一个构建的编号，如果作业不存在或没有构建，则返回 None
        """
        try:
            # 确保作业名称是有效的字符串
            if not isinstance(job_name, str) or not job_name.strip():
                print("无效的作业名称: '{}'".format(job_name))
                return None

            # 检查作业是否存在
            if not self.server.has_job(job_name):
                print("Jenkins作业 '{}' 不存在".format(job_name))
                return None

            # 获取最后一个构建编号
            last_buildnumber = self.server.get_job(job_name).get_last_buildnumber()
            return last_buildnumber

        except JenkinsAPIException as e:
            print("获取Jenkins作业 '{}' 的最后一个构建编号时出错: {}".format(job_name, str(e)))
            return 0

        except Exception as e:
            print("发生未知错误: {}".format(str(e)))
            return 0


