from __future__ import absolute_import
from celery import Celery
import sys
import os

# django.core.exceptions.ImproperlyConfigured: Requested settings,
# but settings are not configured.
# You must either define the environment variable DJANGO_SETTINGS_MODULE or call settings.configure()
# before accessing settings
# 报以上错误就打开下面注释或者在启动celery的时候先设置定义DJANGO_SETTINGS_MODULE变量
# windows启动；设置环境变量： set DJANGO_SETTINGS_MODULE=isesol.setting.settings   启动脚本：celery -A cron worker -l info
# linux启动；设置环境变量： export DJANGO_SETTINGS_MODULE=isesol.setting.settings_prod   启动脚本：celery -A cron worker -B -l info

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'isesol.setting.settings_prod')
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'isesol.setting.settings')

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
app = Celery("cron", include=["cron.tasks"])
app.config_from_object("cron.config")

if __name__ == "__main__":
    app.start()
