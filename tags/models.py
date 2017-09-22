from django.db import models
from django.utils.translation import ugettext_lazy as _

from taggit.models import TagBase, GenericTaggedItemBase


class Tag(TagBase):
    """ A custom tag model to provide a description field to tags.
    """
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")


class TaggedItem(GenericTaggedItemBase):
    tag = models.ForeignKey("Tag", related_name="%(app_label)s_%(class)s_items")
