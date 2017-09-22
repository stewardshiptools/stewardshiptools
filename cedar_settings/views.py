from django.core.urlresolvers import reverse_lazy
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.views.generic import FormView
from django import forms
from .forms import CedarSettingsForm
from .models import GeneralSetting


# Create your views here.
class CedarSettingsView(FormView):
    '''
    Note: Test the data types.
        - if a "reference" type has first been set with a string ie as is the
        case with some HarvestPrefixCodes, this thing probably won't know what to do with that.
        - date/time picker hasn't been set up yet in the form - you'll just get a text field for now.
            - see phonecall_form template for guidance.
    '''
    template_name = 'cedar_settings/settings_form.html'
    form_class = CedarSettingsForm

    '''
    setting_fields = [
        {
            'name': 'blah',
            'data_type': 'reference',
            'queryset': SomeModel.objects.all(),
            'label': 'Test Setting'
        },
        {
            'name': 'blahbool',
            'data_type': 'boolean',
            'label': 'Test Setting'
        },
        {
            'name': 'blahstr',
            'data_type': 'text',
            'label': 'Test Setting'
        },
        {
            'name': 'blahint',
            'data_type': 'int',
            'label': 'Test Setting'
        },
        # ...
    ]
    '''

    setting_fields = []

    def __init__(self, **kwargs):
        super(CedarSettingsView, self).__init__(**kwargs)
        self.setting_fields = self.get_setting_fields()

    def get_setting_fields(self):
        '''
        Override this if you need to do something special.
        :return:
        '''
        return self.setting_fields

    def form_valid(self, form):
        response = super(CedarSettingsView, self).form_valid(form)

        for setting_field in self.setting_fields:
            field_name = setting_field['name']
            field_type = setting_field['data_type']
            if field_name in form.changed_data:
                obj = form.cleaned_data[field_name]
                if obj is not None:
                    GeneralSetting.objects.set(field_name, obj, field_type)
                else:
                    GeneralSetting.objects.filter(name=field_name).delete()
        return response

    def get_form_kwargs(self):
        kwargs = super(CedarSettingsView, self).get_form_kwargs()
        kwargs['setting_fields'] = self.setting_fields
        return kwargs

    def get_initial(self):
        initial = super(CedarSettingsView, self).get_initial()

        for setting_field in self.setting_fields:
            field_name = setting_field['name']
            setting = GeneralSetting.objects.get(field_name)
            initial[field_name] = setting

        return initial

    def get_success_url(self):
        '''
        You need to override this.
        :return:
        '''
        return reverse_lazy("")

    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def dispatch(self, request, *args, **kwargs):
        return super(CedarSettingsView, self).dispatch(request, *args, **kwargs)

