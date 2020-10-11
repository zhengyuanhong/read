from __future__ import absolute_import
from celery import Celery
from celery.schedules import crontab
import os,django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "readDjango.settings")
django.setup()
broder = 'redis://127.0.0.1:6379/2'
backend = 'redis://127.0.0.1:6379/3'

app = Celery('celery_task',
             broker=broder,
             backend=backend,
             include=['celery_task.task']
             )

app.conf.beat_schedule = {
    "each1m_task": {
        "task": "celery_task.task.regNotify",
        "schedule": crontab(minute=1),  # 每1分钟执行一次 也可以替换成 60  即  "schedule": 60
        'args':('test','ddd')
    }
}

if __name__ == '__main__':
    app.start()
