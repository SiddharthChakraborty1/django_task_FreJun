from __future__ import absolute_import, unicode_literals

import os

from celery import Celery

os.environ.setdefault('FORKED_BY_MULTIPROCESSING', '1')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FreJun_task.settings')

app = Celery('FreJun_task')

app.config_from_object('django.conf.settings', namespace='CELERY')

app.autodiscover_tasks()