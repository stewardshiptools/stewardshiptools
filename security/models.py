import ast

from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

from cedar_settings.models import GeneralSetting


class SecurityLevelManager(models.Manager):
    def get_for_object(self, obj):
        """ Take any model instance and try to fetch a related SecurityModel

        :param obj: Any model instance
        :return: a SecurityLevel instance or None if nothing is found.
        """
        try:
            return self.get(
                obj_id=obj.id,
                obj_ct=ContentType.objects.get_for_model(obj)
            )
        except self.model.DoesNotExist:
            return None


class SecurityLevel(models.Model):
    level_choices = ast.literal_eval(GeneralSetting.objects.get('security_level_choices', "[]"))
    level_default = GeneralSetting.objects.get('security_level_default')

    # Default to the highest integer (the lowest permission level)
    level = models.IntegerField(choices=level_choices, default=level_default)

    # If a related object is deleted, delete this SecurityLevel instance as well.
    obj_ct = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    obj_id = models.PositiveIntegerField()
    obj = GenericForeignKey('obj_ct', 'obj_id')

    objects = SecurityLevelManager()
