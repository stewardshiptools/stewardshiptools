from django import forms
from cedar_settings.models import GeneralSetting


class CedarSettingsForm(forms.Form):
    # project_code_prefix = forms.ModelChoiceField(required=False, queryset=HarvestCodePrefix.objects.all())
    def __init__(self, *args, **kwargs):
        setting_fields = kwargs.pop('setting_fields', None)
        assert setting_fields is not None, "setting_fields must be provided"

        super(CedarSettingsForm, self).__init__(*args, **kwargs)

        for setting in setting_fields:
            setting_name = setting['name']
            setting_type = setting['data_type']
            field_class = GeneralSetting.form_field_class(setting_type)

            if setting_type == 'reference':
                field_class = field_class(queryset=setting['queryset'])

            self.fields[setting_name] = field_class

            self.fields[setting_name].label = setting['label']

            if 'required' in setting.keys():
                self.fields[setting_name].required = setting['required']
            else:
                self.fields[setting_name].required = False
