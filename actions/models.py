from django.contrib.gis.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from model_utils.managers import InheritanceManager


def get_default_date_time():
    return timezone.now() + timezone.timedelta(days=7)


class ActionMaster(models.Model):
    """
    This is the Action model that should be passed around
    """
    label = models.CharField(max_length=250)
    date = models.DateTimeField(default=get_default_date_time) # aw and I had a pretty lambda ready for this
    assignee = models.ForeignKey(User, blank=True, null=True, related_name='assigned_actions')
    subscribers = models.ManyToManyField(User, blank=True, related_name='subscribed_actions')
    send_reminder = models.BooleanField(default=False)

    objects = InheritanceManager()

    def __str__(self):
        return "%s - %s" % (self.label, self.date)


class Action(ActionMaster):
    pass
