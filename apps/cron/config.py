from __future__ import absolute_import
from datetime import timedelta
from django.conf import settings

BROKER_URL = settings.BROKER_URL
CELERY_BACKEND_URL = settings.CELERY_BACKEND_URL

CELERYBEAT_SCHEDULE = {
    'check-jenkins-30-seconds': {
        'task': 'cron.tasks.check_jenkins_status',
        'schedule': timedelta(seconds=10),
    },
    'sync-ad-user-1-days': {
        'task': 'cron.tasks.sync_ad_user',
        'schedule': timedelta(days=1),
    },
    # 'password-expr-notice-1-days': {
    #     'task': 'cron.tasks.password_expr_notice',
    #     'schedule': timedelta(days=1),
    # },
}
