from django.conf import settings
from django.db.models.signals import post_save

from crm.models import Person
from django.contrib.auth.models import User


# Catch the crm.Person save signal in order to update
# fields in the related auth.User model:
def person_post_save_update_user(sender, instance, created, **kwargs):
    if instance.user_account:
        # DON'T USE SAVE - it will trigger crazy recursion because
        # it will call the User post_save signal (which will call this one...)
        # Use update instead:
        User.objects.filter(id=instance.user_account.id).update(
            email=instance.email,
            first_name=instance.name_first,
            last_name=instance.name_last)


post_save.connect(person_post_save_update_user, sender=Person)
