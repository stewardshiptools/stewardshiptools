from django.conf import settings
from django.db.models.signals import post_save
from django.contrib.auth.models import Group

from crm.models import Person


def user_post_save_update_crm(sender, instance, created, **kwargs):
    if created:

        # If creating a new user, check if the DEFAULT_USER_GROUP setting exists
        # and add the user to the default group it it does.
        group_name = getattr(settings, 'DEFAULT_USER_GROUP', None)
        if group_name:
            group = Group.objects.get(name=group_name)
            group.user_set.add(instance)

    # Catch the auth.User save signal in order to update
    # fields in the related crm.Person model:
    try:
        person = Person.objects.get(user_account=instance)
    except Person.DoesNotExist:
        person = None

    if person:
        person.email = instance.email
        person.name_first = instance.first_name
        person.name_last = instance.last_name
        person.save()


post_save.connect(user_post_save_update_crm, sender=settings.AUTH_USER_MODEL)
