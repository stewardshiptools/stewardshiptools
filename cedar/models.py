from django.db import models
from cedar.managers import PrefixedIDManager


class PrefixedIDModelAbstract(models.Model):
    """
    Add this mixin and you only need to override the get_prefix() method.
    get_prefix() should return something like:
        - "I-" or "CB-"
        
    This model abstract comes along with the Prefixed ID model manager that automatically annotates
    querysets with the prefixed_id
    """

    objects = PrefixedIDManager()

    @classmethod
    def get_prefix(cls):
        """
        Needs to be a classmethod so that it's accessible from the manager.
        should return a prefix like:
            "I-" or "CB-"
        :return: 
        """
        return ""

    @property
    def prefixed_id(self):
        return self.get_prefix() + str(self.id)

    class Meta:
        abstract = True
