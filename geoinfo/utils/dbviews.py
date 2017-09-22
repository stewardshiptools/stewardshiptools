import logging
from django.conf import settings
from django.db import connection

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


sql_grant_select = 'GRANT SELECT ON "{viewname}" TO {rolename};'


def grant_view_perms_to_users(view_name):
    '''
    Called by management command create db views - exposes view to the predefined user role
    :param view_name:
    :return:
    '''
    if not user_role_exists():
        make_user_role()

    logger.info("grant select on {} to {}".format(view_name, settings.DBVIEWS_USER_ROLE))

    sql = sql_grant_select.format(viewname=view_name, rolename=settings.DBVIEWS_USER_ROLE)
    cursor = connection.cursor()
    cursor.execute(sql)


def user_role_exists():
    '''
    Checks if the defined user role exists.
    :return:
    '''
    sql = "SELECT count(*) FROM pg_roles where rolname = '{rolename}';".format(rolename=settings.DBVIEWS_USER_ROLE)
    c = connection.cursor()
    c.execute(sql)
    result = c.fetchone()
    if result[0] > 0:
        return True
    else:
        return False


def make_user_role():
    logger.info("make user role: {}".format(settings.DBVIEWS_USER_ROLE))
    sql = "CREATE ROLE {rolename};".format(rolename=settings.DBVIEWS_USER_ROLE)
    c = connection.cursor()
    c.execute(sql)
