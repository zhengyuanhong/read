from __future__ import absolute_import
from celery import Celery
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


if __name__ == '__main__':
    app.start()
