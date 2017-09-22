import ast

from django import forms
from django.contrib.contenttypes.models import ContentType
from security.utils import get_security_level_or_default_from_object

from security.models import SecurityLevel
from cedar_settings.models import GeneralSetting


class SecurityLevelModelFormMixin(forms.Form):
    """ Form mixin to be mixed in with a ModelForm.  Make sure the target form doesn't already provide a field named
    'security_level'.

    If using this mixin with an admin form, you have to declare the security_level field as an attribute in the class.
    e.g. security_level = ChoiceField()
    This mixin will take care of adding details.  The admin class just needs to see the field.

    Provides a security_model field that automatically attaches an instance of security.models.SecurityModel to any
    object.
    """
    security_level_default = GeneralSetting.objects.get('security_level_default')

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)

        super().__init__(*args, **kwargs)

        level_choices = ast.literal_eval(GeneralSetting.objects.get('security_level_choices', "[]"))

        if user:
            # Only allow users to set security levels at or below their own level.
            if not user.is_superuser:
                user_level = get_security_level_or_default_from_object(user)
                level_choices = filter(lambda x: x[0] >= user_level, level_choices)

        security_level = SecurityLevel.objects.get_for_object(self.instance)
        if security_level is None:
            level_default = self.get_security_level_default()
        else:
            level_default = security_level.level

        self.fields['security_level'] = forms.ChoiceField(
            label='Security level',
            choices=level_choices,
            initial=level_default
        )

    def save(self, commit=True):
        """ If this is called with commit=False you must call the create_security_level_for_object method with the
        object after it's been saved.
        
        :param commit:
        :return:
        """
        instance = super().save(commit=False)

        if commit:
            instance.save()

        if instance.id:
            self.create_security_level_for_object(instance)

        return instance

    def create_security_level_for_object(self, obj):
        security_level_value = self.cleaned_data['security_level']
        try:
            security_level = SecurityLevel.objects.get(
                obj_id=obj.id,
                obj_ct=ContentType.objects.get_for_model(obj)
            )
        except SecurityLevel.DoesNotExist:
            security_level = SecurityLevel(obj=obj)

        security_level.level = security_level_value
        security_level.save()
        return security_level

    def get_security_level_default(self):
        return self.security_level_default
