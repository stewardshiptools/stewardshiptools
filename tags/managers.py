from django import forms
from django.utils.translation import ugettext_lazy as _
from taggit.managers import TaggableManager as BaseTaggableManager
from taggit.forms import TagField, TagWidget
from taggit.utils import edit_string_for_tags, parse_tags


class TagFieldExtended(forms.CharField):
    widget = TagWidget

    def clean(self, value):
        value = super().clean(value)
        try:
            return parse_tags(value)
        except ValueError:
            raise forms.ValidationError(
                _("Please provide a comma-separated list of tags."))


class TaggableManagerExtended(BaseTaggableManager):
    """
    Extended for cedar 8.
    """

    def __init__(self, *args, **kwargs):
        self.belongs_to = kwargs.pop('belongs_to', None)
        super().__init__(*args, **kwargs)

    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset(*args, **kwargs)
        if self.belongs_to:
            qs = qs.filter(belongs_to=self.belongs_to)
        return qs

    # def formfield(self, form_class=TagFieldExtended, **kwargs):
    #     defaults = {
    #         "label": _("Tags"),
    #         "help_text": _("A comma-separated list of tags."),
    #         "required": not self.blank,
    #
    #     }
    #     defaults.update(kwargs)
    #
    #     return form_class(**defaults)
    #
