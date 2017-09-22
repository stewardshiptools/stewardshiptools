# cedar_settings/models.py
""" A set of models and a custom manager for implementing general settings system.
Any other app in cedar that just needs to store some configurable value can store it as a general setting.

Basic use:

>>> from cedar_settings.models import GeneralSetting
>>> foo = {'b': 'asdf', 'c': 'fdsa'}
>>> GeneralSetting.objects.set('test_json', foo, 'json')
>>> GeneralSetting.objects.get('test_json')
{'b': 'asdf', 'c': 'fdsa'}
>>> GeneralSetting.objects.get('test_json')['b']
'asdf'

>>> GeneralSetting.objects.set('about_settings', 'Settings are useful and awesome!', 'text')
>>> GeneralSettings.objects.get('about_settings')
'Settings are useful and awesome!'

Dates....
>>> from datetime import datetime
>>> from cedar_settings.models import GeneralSetting
>>> from cedar_settings.utils.datetime import localize_datetime
date = datetime(2015, 5, 25, 20, 35, 21)
>>> GeneralSetting.objects.set('test_date', localize_datetime(date), 'date')
>>> GeneralSetting.objects.get('test_date')
datetime.datetime(2015, 5, 26, 3, 35, 21, tzinfo=<UTC>)
# Note it translated the datetime into UTC before storing.
"""
from django.db import models
from django.db.utils import ProgrammingError
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.forms.models import fields_for_model
from django import forms

from django_hstore import hstore

from .utils.defaults import get_default_settings


class SettingManager(models.Manager):
    def set(self, name, value, data_type='text'):
        """
        Attempt to set the value of a setting.  If the setting doesn't exist, create it.

        :param name: The name of the setting.
        :param value: The value to set.
        :param data_type: the data_type of the setting.
        :return:
        """
        try:
            obj = super(SettingManager, self).get(name=name)
        except self.model.DoesNotExist:
            obj = self.model(name=name, data_type=data_type)

        return obj.set(value, data_type)

    def get(self, name, default=None, *args, **kwargs):
        try:
            kwargs['name'] = name
            obj = super(SettingManager, self).get(*args, **kwargs)
            return obj.value
        except self.model.DoesNotExist:
            # Get a default.
            if default is not None:
                return default
            else:
                default_value = self.model.default_settings().get(name, None)
                if default_value is None:
                    return None
                else:
                    return default_value[1]
        except ProgrammingError:
            pass  # A Programming error can occur when this exists in code that is called before cedar_settings
            # migrations have been run.


class Setting(models.Model):
    data_types = (
        ('text', 'Text'),
        ('int', 'Integer'),
        ('float', 'Float'),
        ('boolean', 'Boolean'),
        ('date', 'Date'),
        ('json', 'JSON'),
        ('reference', 'Reference')
    )

    name = models.CharField(max_length=200, unique=True, primary_key=True)

    data_type = models.CharField(choices=data_types, default='text', max_length=200)

    text_value = models.TextField(blank=True, null=True)
    int_value = models.IntegerField(blank=True, null=True)
    float_value = models.FloatField(blank=True, null=True)
    boolean_value = models.BooleanField(default=False)
    date_value = models.DateTimeField(blank=True, null=True)
    json_value = hstore.DictionaryField(blank=True, null=True)

    reference_ct = models.ForeignKey(ContentType, blank=True, null=True)
    reference_id = models.PositiveIntegerField(blank=True, null=True)
    reference_value = GenericForeignKey('reference_ct', 'reference_id')

    objects = SettingManager()

    def __str__(self):
        return self.name

    @property
    def _attr(self):
        '''
        Use ths instead of doing string replacements elsewhere.
        Needed a static/non static version of this method.
        :return: the internal model field name.
        '''
        return Setting.attr(self.data_type)

    @staticmethod
    def attr(data_type):
        '''
        Needed a static/non static version of this method.
        :param data_type:
        :return: the internal model field name.
        '''
        return '{}_value'.format(data_type)

    @property
    def value(self):
        return getattr(self, self._attr)

    def set(self, value, data_type=None):
        """
        A helper method to update settings.  This method requires that at least the data_type field has been set.
        There is no error checking for this yet.  It is up to the implementer to pass a value appropriate for the
        setting being set.

        :param name: The name of the setting to set.
        :param value: The value of the setting to set.
        :return: The result of self.save()
        """
        if data_type is None:
            data_type = self.data_type

        if data_type == 'reference':  # value must be an instance of a model.
            self.reference_value = value
        else:
            setattr(self, self._attr, value)

        # Make sure the data_type is up to date
        self.data_type = data_type

        return self.save()

    @staticmethod
    def default_settings():
        return dict()

    @staticmethod
    def form_field_class(data_type):
        # exception for reference field
        if data_type == 'reference':
            return forms.models.ModelChoiceField
        else:
            internal_field_name = Setting.attr(data_type)
            return fields_for_model(Setting)[internal_field_name]

    class Meta:
        abstract = True


class GeneralSetting(Setting):
    @staticmethod
    def default_settings():
        return get_default_settings()
