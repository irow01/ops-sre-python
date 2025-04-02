from __future__ import absolute_import
import os
import sys
import json
from cron.celery import app
from django.core.cache import cache
from utils import jenkinsModel
from utils import ADHelper
from user.models import User
from utils import SendMail
import datetime
import re

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))


# django.core.exceptions.ImproperlyConfigured: Requested settings,
# but settings are not configured.
# You must either define the environment variable DJANGO_SETTINGS_MODULE or call settings.configure()
# before accessing settings
# 报以上错误就打开下面注释或者在启动celery的时候先设置定义DJANGO_SETTINGS_MODULE变量
# windows启动；设置环境变量： set DJANGO_SETTINGS_MODULE=isesol.setting.settings   启动脚本：celery -A cron worker -l info
# linux启动；设置环境变量： export DJANGO_SETTINGS_MODULE=isesol.setting.settings_prod   启动脚本：celery -A cron worker -B -l info


# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'isesol.setting.settings_prod')
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'isesol.setting.settings')




@app.task
def check_jenkins_status():
    plist = cache.get("plist")
    Jk = jenkinsModel.JenkinsModel()
    if plist is None:
        return False
    plist = json.loads(plist)
    # 如果plist为空列表时，此时没有发布任务
    if len(plist['pid']) == 0:
        return True

    # 循环plist中的工单ID
    for pid in plist['pid']:
        # 通过plist中获取到的工单ID，获取每个工单的发布key
        deploy_str = cache.get("deploy" + str(pid))
        deploy_dict = json.loads(deploy_str)

        # 如果工单key的status状态为True，此时发布成功
        if deploy_dict["status"]:
            continue

        # 定义局部标识位, 用于最终修改工单key的状态。
        deploy_flag = True
        deploy_none_flag = True

        # 循环工单key中的job_list字段，获取到每个job任务
        for job_name, job_status in deploy_dict['job_list'].items():
            status = job_status["status"]

            # 只有未发布(0)或发布失败的任务(1)才会进入发布流程中
            if status == 0 or status == 1:
                jenkins_queue_number = job_status["job_id"]
                jenkins_build_info = {}
                jenkins_build_number = 0

                if status == 0:
                    # 判断redis队列中的项目是否在构建或排队中
                    try:
                        jenkins_build_info = Jk.get_queue_item(job_name)
                    except Exception as e:
                        print("任务: {}, 检查队列状态时出错: {}".format(job_name, str(e)))
                    if not jenkins_build_info:
                        try:
                            jenkins_build_number = Jk.get_last_buildnumber(job_name)
                        except Exception as e:
                            print("无法获取任务编号，任务可能仍在排队中: {}".format(str(e)))
                    else:
                        print("任务: {}, 队列编号: {} , 请求超时,任务不存在".format(job_name, jenkins_queue_number))
                elif status == 1:
                    jenkins_build_number = deploy_dict["job_list"][job_name]['job_id']

                print(jenkins_build_number)
                if jenkins_build_number != 0:
                    jenkins_deploy_status = Jk.get_build_status(job_name, jenkins_build_number)
                    print(jenkins_deploy_status)
                    if jenkins_deploy_status == "FAILURE":
                        deploy_dict["job_list"][job_name]['status'] = 2  # 标记任务发布失败
                        deploy_dict["job_list"][job_name]['job_id'] = jenkins_build_number
                    # elif jenkins_deploy_status == "None":
                    #     deploy_dict["job_list"][job_name]['status'] = 1  # 标记任务发布中
                    elif jenkins_deploy_status == "SUCCESS":
                        deploy_dict["job_list"][job_name]['status'] = 3  # 标记任务发布成功
                        # 当发布成功后，将工单key对应job的build number记录下来
                        deploy_dict["job_list"][job_name]['job_id'] = jenkins_build_number
                    else:
                        deploy_dict["job_list"][job_name]['job_id'] = jenkins_build_number
                        deploy_dict["job_list"][job_name]['status'] = 1  # 标记任务发布中

        for _, v in deploy_dict['job_list'].items():
            if v['status'] != 3:
                deploy_flag = False
                break

        # 确保有发布任务并且发布都成功才将key重写到redis
        if deploy_flag:
            deploy_dict['status'] = True

        cache.set("deploy" + str(pid), json.dumps(deploy_dict), timeout=None)

        print(deploy_dict)

        if deploy_dict['status']:
            plist['pid'].remove(pid)
            print(plist)
            # 使用nx锁, 防止前端用户提交发布任务时，导致重复写
            if cache.set("lock", "true", nx=True, timeout=1):
                cache.set("plist", json.dumps(plist), timeout=None)
    return plist


@app.task
def sync_ad_user():
    user = ADHelper.AD()
    status, user_list = user.get_user()
    if status:
        for user in user_list:
            user_obj = dict()
            user_obj['username'] = user[1]
            user_obj['nickname'] = user[0]
            user_obj['email'] = user[2]
            user_obj['department'] = user[3]
            user_obj['account_expr'] = user[4]
            if not user_obj['email']:
                continue
            #if not re.match('.*isesol.com', user[2]):
            #    continue
            obj = User.objects.filter(email=user[2]).first()
            if not obj:
                User.objects.create(**user_obj)
            else:
                obj.account_expr = user[4]
                obj.save()

    else:
        print("获取用户信息失败.")


@app.task
def password_expr_notice():
    now_date = datetime.date.today()
    user_obj = User.objects.all()
    for user in user_obj:
        user_expr_date = user.account_expr - now_date
        if user_expr_date < datetime.timedelta(days=7):
            email_dict = dict()
            email_dict['to_mail'] = user.email
            email_dict['sub'] = '密码过期提醒'
            mail_obj = SendMail.SendMail(email_dict)
            mail_obj.send_mail()
