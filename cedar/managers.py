from django.db import models
from django.db.models.functions import Concat
from django.db.models import Q, F, Value, CharField


class PrefixedIDManager(models.Manager):
    def get_queryset(self):
        '''
        Override get_queryset to annotate objects with the prefixed_id_q field
        :return:
        '''
        qs = super().get_queryset()

        return qs.annotate(
            prefixed_id_q=Concat(
                Value("{}".format(self.model.get_prefix())),
                F('id'),
                output_field=CharField()
            )
        )
