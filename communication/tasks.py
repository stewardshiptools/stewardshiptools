from __future__ import absolute_import
import logging
import time
from django.core.cache import cache  # , get_cache
from contextlib import contextmanager
from celery import shared_task, chord, group, task
from celery.five import monotonic

from communication.models import MailAccount, Mailbox

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# TODO find a good way to return the results of subtasks from parent tasks.

# http://ask.github.io/celery/cookbook/tasks.html#ensuring-a-task-is-only-executed-one-at-a-time
# http://stackoverflow.com/questions/29355613/run-a-chord-callback-even-if-the-main-tasks-fail?rq=1

LOCK_EXPIRE = 30  # seconds


@shared_task()
def harvest_mail_DEPRECATED():
    '''
    Run harvest async on ALL activate mailboxes
    This is actually the preferred method of executing mail harvest. This way
    the task-mon will see that harvests are being run on individual accounts and
    respond accordingly. BUT, there is some weird issue with the task id always
    saying "PENDING" even when it's not - when checked by the celery status check view.
    The regular check_task_mail_account_status_all() DOES return the task id & status as expected.
    :return: celery worflow.id
    '''
    lock_id = "lock:{}".format(harvest_mail.name)

    # logger.info("Attempting to run harvest_mail on all mailboxes")

    if cache.add(lock_id, "true", LOCK_EXPIRE):
        try:
            logger.debug("lock aquired for \"{}\"".format(lock_id))

            mailboxes = Mailbox.objects.filter(active=True)

            mail_accounts = MailAccount.objects.all()
            workflow = group(harvest_mail_account.s(ma.id) for ma in mail_accounts)
            res = workflow.apply_async(id='mail-harvest-runner-all')

            # Update the cache lock with the id of the worflow.
            logger.debug("updating cache with id of the res: {}".format(workflow.id))
            cache.set(lock_id, res.id, LOCK_EXPIRE)
        finally:
            # logger.debug("start sleep")
            # time.sleep(20)
            # logger.debug("end sleep")
            # logger.debug("workflow.id:{}".format(workflow.id))
            return res.id
    else:
        logger.debug("Not able to acquire task lock for lock-id \"{}\"".format(lock_id))
        # return the workflow id from the cache so the browser can track progress:
        return cache.get(lock_id)


@shared_task()
def harvest_mail():
    '''
    Run harvest async on ALL activate mailboxes
    :return: celery worflow.id
    '''
    lock_id = "lock:{}".format(harvest_mail.name)

    # logger.info("Attempting to run harvest_mail on all mailboxes")

    if cache.add(lock_id, "true", LOCK_EXPIRE):
        try:
            logger.debug("lock aquired for \"{}\"".format(lock_id))

            mailboxes = Mailbox.objects.filter(active=True)

            # create chord:
            cho = chord(harvest_mailbox.s(mb.id) for mb in mailboxes)

            # run chord and set callback with unlock and sum method:
            workflow = cho(
                unlock_and_sum.s(
                    **{'lock_id': lock_id}
                ))

            # Update the cache lock with the id of the worflow.
            cache.set(lock_id, workflow.id, LOCK_EXPIRE)
        finally:
            # logger.debug("start sleep")
            # time.sleep(20)
            # logger.debug("end sleep")
            # logger.debug("workflow.id:{}".format(workflow.id))
            return workflow.id
    else:
        logger.debug("Not able to acquire duplicate task lock for lock-id \"{}\"".format(lock_id))
        # return the workflow id from the cache so the browser can track progress:
        return cache.get(lock_id)


@shared_task()
def harvest_mail_account(mail_account_id):
    '''
    Run harvest async on a particular mail_account
    :param mail_account_id: id of the mail account to harvest.
    :return: celery worflow.id
    '''
    lock_id = "lock:{}:{}".format(harvest_mail_account.name, mail_account_id)

    logger.info("Attempting to run harvest_mail for id:{}".format(mail_account_id))
    # logger.info("lock_id  \"{}\"".format(lock_id))

    if cache.add(lock_id, "true", LOCK_EXPIRE):
        try:
            logger.debug("lock aquired for \"{}\"".format(lock_id))
            mail_account = MailAccount.objects.get(id=mail_account_id)
            mailboxes = mail_account.mailbox_set.filter(active=True)

            # create chord:
            cho = chord(harvest_mailbox.s(mb.id) for mb in mailboxes)

            # run chord and set callback with unlock and sum method:
            workflow = cho(
                unlock_and_sum.s(
                    **{'lock_id': lock_id}
                ))

            # Update the cache lock with the id of the worflow.
            cache.set(lock_id, workflow.id, LOCK_EXPIRE)
        finally:
            # logger.debug("start sleep")
            # time.sleep(20)
            # logger.debug("end sleep")
            # logger.debug("workflow.id:{}".format(workflow.id))
            return workflow.id
    else:
        logger.debug("Not able to acquire duplicate task lock for lock-id \"{}\"".format(lock_id))
        # return the workflow id from the cache so the browser can track progress:
        return cache.get(lock_id)


@shared_task()
def harvest_mailbox(mailbox_id):
    try:
        mailbox = Mailbox.objects.get(id=mailbox_id)
        new_mail = mailbox.harvest_mail()
    except ConnectionError:
        logger.error("mailbox {} for account {} raise a ConnectionError.".format(mailbox.id, mailbox.mail_account.id))
        return 0
    return len(new_mail)


@shared_task()
def xsum(x):
    return sum(x)


@task(name='super_task.unlock_and_sum')
def unlock_and_sum(*args, **kwargs):
    '''
    Unlocks the task in the cache and returns the sum of the harvest task return values.
    :param args:
    :param kwargs:
    :return:
    '''
    # logger.debug('unlock')
    # logger.debug(args)
    # logger.debug(kwargs)
    lock_id = kwargs.get('lock_id')
    cache.delete(lock_id)
    logger.debug("lock released for \"{}\".".format(lock_id))
    return sum(args[0])
