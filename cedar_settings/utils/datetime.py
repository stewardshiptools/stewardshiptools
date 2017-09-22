import pytz

from django.conf import settings


def localize_datetime(dt):
    """ Takes a datetime object and localizes it to the timezone saved in settings.TIME_ZONE

    :param dt: datetime object
    :return: Timezone aware datetime object
    """
    tz = pytz.timezone(settings.TIME_ZONE)
    return tz.localize(dt)
