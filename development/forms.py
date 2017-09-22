from datetime import datetime
from django import forms
from django.forms.models import inlineformset_factory
from phonenumber_field.formfields import PhoneNumberField
from mptt.forms import TreeNodeChoiceField

from .models import DevelopmentProject, DevelopmentGISLayer, DevelopmentProjectAsset, FileNo, DevelopmentAsset, \
    DevelopmentProjectAction, ConsultationStage, FilingCode

from communication.models import HarvestCodePrefix

from tags.widgets import TagAutoSuggestSelect2

from cedar_settings.models import GeneralSetting
from cedar_settings.utils.parsers import parse_choices

from geoinfo.forms import GISLayerForm, GeneralSpatialReportForm

from assets.forms import SecureAssetForm


class DevelopmentSettings(forms.Form):
    project_code_prefix = forms.ModelChoiceField(required=False, queryset=HarvestCodePrefix.objects.all())


class DevelopmentProjectForm(forms.ModelForm):
    """
    Used by:
        DevelopmentProjectCreateView
        DevelopmentProjectUpdateView
        DevelopmentProjectCreateFromSERView
    """
    primary_authorization = forms.ChoiceField(required=False)
    filing_code = TreeNodeChoiceField(queryset=FilingCode.objects.all())

    # hidden fields used by DevelopmentProjectCreateFromSERView to create geomark layers from xml.
    geomark_url = forms.CharField(required=False)
    geomark_notes = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        super(DevelopmentProjectForm, self).__init__(*args, **kwargs)

        primary_auth_choices = parse_choices(GeneralSetting.objects.get('development_project_primary_auth_choices'))
        self.fields['primary_authorization'].choices = primary_auth_choices

        # Parse the development_project_misc_textareas setting and create multiple text areas
        textarea_names = parse_choices(GeneralSetting.objects.get('development_project_misc_textareas'), False)

        # Iterate over misc text areas and dynamically create fields for them.
        for name in textarea_names:
            if name and name[0] and name[1]:
                self.fields["misc_textarea_%s" % name[0]] = forms.CharField(label=name[1],
                                                                            widget=forms.Textarea, required=False)
        if self.instance.id is None:
            self.fields['consultation_stage'].initial = ConsultationStage.objects.first()

        # set widget placeholder texts - it would be great if this could go where I would expect it: in Meta.
        self.fields['cedar_project_name'].widget.attrs.update({'placeholder': 'LOCATION-PROPONENT-AUTHORIZATION-{}'.format(datetime.now().strftime('%Y.%m.%d.'))})

    def save(self, commit=True):
        # TODO should this be commit=False?
        obj = super(DevelopmentProjectForm, self).save(commit=commit)

        # Misc text areas
        hstore_dict = obj.misc_textareas

        # Retrieve the misc text area sections from general settings.
        textarea_names = parse_choices(GeneralSetting.objects.get('development_project_misc_textareas'), False)

        # Iterate through the text area fields and add the resulting dictionary to the project hstore field.
        for name in textarea_names:
            if name and name[0] and name[1]:
                field_name = "misc_textarea_%s" % name[0]
                hstore_dict[name[1]] = self.cleaned_data[field_name]

        obj.misc_textareas = hstore_dict

        if commit:
            obj.save()
        return obj

    class Meta:
        model = DevelopmentProject
        fields = '__all__'
        # exclude = ['cedar_project_code',]

        widgets = {
            'tags': TagAutoSuggestSelect2(tagmodel='tags.Tag', min_input=0)
        }

        # TODO Come up with a prettier format for materializecss help text.
        # Using this here to override ugly help text.
        help_texts = {
            'initial_date': "",
        }


class DevelopmentProjectGISLayerForm(GISLayerForm):
    '''
    Small note: this form requires that a devt project is given when the form
    is instantiated, hides that input on the form, and validates against it.
    '''

    development_project_instance = None  # We don't care what the user inputs, we only are interested in the preset development_project_instance.

    def __init__(self, *args, **kwargs):
        # Restrict project field to the actual project this layer will belong to. This must
        # be popped off before the super is called:
        dev_project_id = kwargs.pop('dev_project_id', None)
        super(DevelopmentProjectGISLayerForm, self).__init__(*args, **kwargs)

        if dev_project_id is not None:
            self.fields['project'].queryset = DevelopmentProject.objects.filter(id=dev_project_id)
            self.fields['project'].initial = DevelopmentProject.objects.get(id=dev_project_id)
            self.development_project_instance = self.fields['project'].initial  # save for later clean_project method

            # If this form is creating a NEW gis layer, grab the development project code and prepopulate the
            # layer name with that:
            devt_gis_layer = kwargs.pop('instance', None)
            if devt_gis_layer is None:
                self.fields['name'].initial = DevelopmentGISLayer.suggest_layer_name(self.development_project_instance)

    # Double check that the project is what it is supposed to be.
    def clean_project(self):
        data = self.cleaned_data['project']
        if data != self.development_project_instance:
            raise forms.ValidationError("Development Project must be set to:", str(self.development_project_instance))
        return data

    # This little ditty here overrides the form superclass fields
    # and adds in the project.
    class Meta(GISLayerForm.Meta):
        model = DevelopmentGISLayer
        fields = GISLayerForm.Meta.fields + ('project',)


class DevelopmentAssetForm(SecureAssetForm):
    class Meta:
        model = DevelopmentAsset
        fields = SecureAssetForm.Meta.fields


class DevelopmentProjectAssetForm(SecureAssetForm):
    development_project_instance = None  # We don't care what the user inputs, we only are interested in the preset development_project_instance.

    def __init__(self, *args, **kwgargs):
        # Restrict project field to the actual project this layer will belong to. This must
        # be popped off before the super is called:
        dev_project_id = kwgargs.pop('dev_project_id', None)
        if dev_project_id is None:
            raise TypeError('dev_project_id is a required kwarg of DevelopmentProjectGISLayerForm')

        super(DevelopmentProjectAssetForm, self).__init__(*args, **kwgargs)

        self.fields['project'].queryset = DevelopmentProject.objects.filter(id=dev_project_id)
        self.fields['project'].initial = DevelopmentProject.objects.get(id=dev_project_id)
        self.development_project_instance = self.fields['project'].initial  # save for later clean_project method

    # Double check that the project is what it is supposed to be.
    def clean_project(self):
        data = self.cleaned_data['project']
        if data != self.development_project_instance:
            raise forms.ValidationError("Development Project must be set to:", str(self.development_project_instance))
        return data

    class Meta(SecureAssetForm.Meta):
        model = DevelopmentProjectAsset
        fields = SecureAssetForm.Meta.fields + ('project',)


class DevelopmentSpatialReportForm(GeneralSpatialReportForm):
    def get_item_choices(self):
        items = super(DevelopmentSpatialReportForm, self).get_item_choices()
        items.append(('development_projects', 'All Development Projects'))
        return items


class FileNoForm(forms.ModelForm):
    class Meta:
        model = FileNo
        fields = '__all__'


class SERForm(forms.Form):
    govt_rep_name_first = forms.CharField(required=True, label="First Name")
    govt_rep_name_last = forms.CharField(required=True, label="Last Name")
    govt_rep_position = forms.CharField(required=False, label="Position")
    govt_rep_email = forms.EmailField(required=True, label="Email")
    govt_rep_phone_number = PhoneNumberField(required=False, label="Phone")
    govt_rep_mailing_address = forms.CharField(widget=forms.Textarea, required=False, label="Mailing Address")
    proposal_short_summary = forms.CharField(widget=forms.Textarea, required=True, label="Description",
                                             help_text='Provide a full description of the Project/Application')
    applicant_company_name = forms.CharField(required=True, label='Company Name')
    applicant_rep_first_name = forms.CharField(required=True, label="First Name")
    applicant_rep_last_name = forms.CharField(required=True, label="Last Name")
    applicant_rep_email = forms.EmailField(required=True, label="Email")
    applicant_rep_phone_number = PhoneNumberField(required=False, label="Phone")
    applicant_rep_mailing_address = forms.CharField(widget=forms.Textarea, required=True, label="Mailing Address")
    bc_filing_code_n = forms.CharField(required=False, label="Government Filing Codes (Separate with commas)")
    applicant_filing_code_n = forms.CharField(required=False, label="Applicant Filing Codes (Separate with commas)")
    location_general_desc = forms.CharField(widget=forms.Textarea, required=True, label="Location General Description")
    location_n_legal_desc = forms.CharField(widget=forms.Textarea, required=False, label="Location Legal Description")
    location_n_geomark = forms.URLField(required=False, label="Geomark URL")
    location_n_geomark_comment = forms.CharField(required=False, label="Geomark Comment")
    location_n_size = forms.CharField(required=False, label="Location Size")  # NOT SHOWN ON FORM
    primary_authorization_type = forms.ChoiceField(required=False, label="Primary Authorization Type")
    authorization_n_name = forms.CharField(required=False, label="Authorization Name")
    authorization_n_description = forms.CharField(widget=forms.Textarea, required=False, label="Authorization Description")
    engagement_lvl_bc_proposed = forms.CharField(required=False, label='Proposed Engagement Level')  # NOT SHOWN ON FORM
    engagement_lvl_bc_rationale = forms.CharField(widget=forms.Textarea, required=False,
                                                  label='Engagement Level Rationale (Optional)',
                                                  help_text=' If you are suggesting an Engagement Level, '
                                                            'please state the poposed level and a rationale '
                                                            'for this level of engagement')
    info_sharing_bc = forms.CharField(widget=forms.Textarea, required=False, label="Info Sharing",
                                      help_text="Provide any information that you have pertaining to"
                                                " impact of the proposed Project/Permit on the Nation and Territory")
    bc_initial_recommendations = forms.CharField(widget=forms.Textarea, required=False, label="Initial Government Recommendations")  # NOT SHOWN ON FORM
    project_rationale = forms.CharField(widget=forms.Textarea, required=False, label='Project Rationale')

    # new fields:
    due_date = forms.DateField(required=False, label='Project Due Date')
    title = forms.CharField(required=True, label='Short Title of Project/Application')

    # for when they reuse an xml doc as a template:
    template_document = forms.FileField(required=False, label="XML Document")

    def __init__(self, *args, **kwargs):
        if kwargs.get('initial', None):
            due_date_initial = kwargs['initial'].get('due_date', None)
            if due_date_initial:
                kwargs['initial'].update({'due_date': datetime.strptime(due_date_initial, '%Y-%m-%d').date()})

        super(SERForm, self).__init__(*args, **kwargs)
        primary_auth_choices = parse_choices(GeneralSetting.objects.get('development_project_primary_auth_choices'))
        self.fields['primary_authorization_type'].choices = primary_auth_choices

        # check and fix due_date -> if it came from an xml file upload then it will be a string but needs to
        # be a datetime object:

        self.fields['title'].widget.attrs.update({'placeholder': 'LOCATION-PROPONENT-AUTHORIZATION-{}'.format(datetime.now().strftime('%Y.%m.%d.'))})


##########################################################################################

# DEPRECATED:
# Makes a separate form for inlines because the draw widget doesn't
# seem to work well in an inline.
class DevelopmentGISLayerInlineForm(forms.ModelForm):
    # Override init so we can make the file field required:
    def __init__(self, *args, **kwargs):
        super(DevelopmentGISLayerInlineForm, self).__init__(*args, **kwargs)
        self.fields['file'].required = True

    class Meta:
        model = DevelopmentGISLayer
        exclude = ('input_type', 'wkt', 'draw', 'author')

        help_texts = {
            'file': "Select a zipped shapefile"
        }

        labels = {
            'file': "Shapefile",
            'name': "Layer name"
        }

DevelopmentGISLayerInlineFormset = inlineformset_factory(DevelopmentProject,
                                                         DevelopmentGISLayer,
                                                         form=DevelopmentGISLayerInlineForm,
                                                         extra=1)
