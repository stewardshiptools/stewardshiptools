from __future__ import absolute_import
import os
from celery import shared_task, chord, group

from django.core import management

# TODO find a good way to return the results of subtasks from parent tasks.


@shared_task()
def update_index(age=2):
    '''
    Runs the asset updater
    :param age: will index documents only <age>-hours old.
    :return:
    '''
    with open(os.devnull, 'w') as f:
        management.call_command('update_index', remove=True, age=age, stdout=f)

