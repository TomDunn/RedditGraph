from __future__ import absolute_import
from os import environ

from celery import Celery

celery = Celery('tasks.config.celery',
                broker=environ['BROKER_URL'],
                backend=environ['CELERY_RESULT_BACKEND'],
                include=['tasks.get_comments',
                         'tasks.get_subreddits',
                         'tasks.crawl',
                         'tasks.get_posts'])

celery.conf.update(
    CELERY_TASK_RESULT_EXPIRES=3600,
    CELERY_ACCEPT_CONTENT=['json'],
    CELERY_TASK_SERIALIZER='json',
    CELERY_RESULT_SERIALIZER='json',
    CELERYD_CONCURRENCY=1,
    #CELERYD_PREFETCH_MULTIPLIER=1
)

if __name__ == '__main__':
    celery.start()
