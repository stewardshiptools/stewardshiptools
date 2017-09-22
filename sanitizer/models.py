from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class SensitivePhraseAbstract(models.Model):
    phrase = models.CharField(max_length=200)
    replace_phrase = models.CharField(max_length=200, blank=True, null=True)
    check_for_word_boundary_start = models.BooleanField(default=True)
    check_for_word_boundary_end = models.BooleanField(default=True)

    def __str__(self):
        return self.phrase

    class Meta:
        abstract = True


class SensitivePhrase(SensitivePhraseAbstract):
    pass

    class Meta:
        ordering = ('-id', 'phrase')


class RelatedSensitivePhrase(SensitivePhraseAbstract):
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    obj = GenericForeignKey('content_type', 'object_id')

    class Meta:
        ordering = ('-id', 'phrase')
