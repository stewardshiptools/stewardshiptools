from datetime import datetime
from django.utils import timezone
from django import forms
# from django.contrib.admin import widgets
# from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404

from leaflet.forms.widgets import LeafletWidget
from tags.widgets import TagAutoSuggestSelect2

from .models import Project, ProjectAsset, Interview, InterviewAsset, LayerGroup, HeritageGISLayer, HeritageAsset,\
    Place, AlternatePlaceName, CommonPlaceName

from assets.forms import SecureAssetForm

from geoinfo.forms import GISLayerForm


class ProjectForm(forms.ModelForm):
    # Not needed for Heritage app.
    # shapefile = forms.FileField(help_text="Upload a spatial data file for this project location.")


    class Meta:
        model = Project
        # fields = '__all__'
        fields = ['name', 'picture', 'phase_code', 'start_date', 'end_date', 'location', 'background']

        # TODO Come up with a prettier format for materializecss help text.
        # Using this here to override ugly help text.
        help_texts = {
            'phase_code': ""
        }


class InterviewForm(forms.ModelForm):
    '''
    Splits the datetime field into two fields managed by separate materialized widgets:
        time_picker, date_picker.
    '''
    time_picker = forms.TimeField(
        label='Time',
        initial=timezone.localtime(timezone.now()).time().strftime('%I:%M%p'),
        input_formats=[
            '%H:%M:%S',  # '14:30:59'
            '%H:%M',  # '14:30',
            '%I:%M%p',  # '5:30 AM',
        ]
    )
    date_picker = forms.DateField(
        label='Date',
        initial=timezone.now().date()
    )

    def __init__(self, *args, **kwargs):
        project_pk = kwargs.pop('project_pk', None)
        super(InterviewForm, self).__init__(*args, **kwargs)

        # set date field to not required, we will set it's value in the clean via the time/date picker values.
        self.fields['date'].required = False

        if project_pk:
            self.fields['phase'].queryset = Project.objects.filter(pk=project_pk)

            # Raise 404 if the project doesn't exist.
            self.fields['phase'].initial = get_object_or_404(Project, pk=project_pk)
            self.project_instance = self.fields['phase'].initial

    def clean_phase(self):
        data = self.cleaned_data['phase']
        if data != self.project_instance:
            raise forms.ValidationError("Project must be set to:", str(self.project_instance))

        return data

    def clean_primary_interviewer(self):
        data = self.cleaned_data['primary_interviewer']
        if data is None:
            raise forms.ValidationError("This field is required")
        return data

    def clean_date(self):
        date = self.cleaned_data.get("date_picker")
        time = self.cleaned_data.get("time_picker")
        try:
            date_and_time = datetime.combine(date, time)
            return date_and_time
        except TypeError as err:
            raise forms.ValidationError("Failed to validate datetime:", str(err))

    class Meta:
        model = Interview
        # fields = '__all__'
        fields = ('phase', 'date_picker', 'time_picker', 'date', 'primary_interviewer', 'other_interviewers', 'participant_number',
                  'community', 'type', 'participants', 'attendees', )


class LayerGroupForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        interview_pk = kwargs.pop('interview_pk', None)
        super(LayerGroupForm, self).__init__(*args, **kwargs)

        # self.fields['primary_interviewer']

        if interview_pk:
            self.fields['interview'].queryset = Interview.objects.filter(pk=interview_pk)

            # Raise 404 if the project doesn't exist.
            self.fields['interview'].initial = get_object_or_404(Interview, pk=interview_pk)
            self.interview_instance = self.fields['interview'].initial

    def clean_interview(self):
        data = self.cleaned_data['interview']
        if data != self.interview_instance:
            raise forms.ValidationError("Interview must be set to:", str(self.interview_instance))

        return data

    class Meta:
        model = LayerGroup
        fields = '__all__'


# Small note: this form requires that a devt project is given when the form
# is instantiated, hides that input on the form, and validates against it.
class HeritageGISLayerForm(GISLayerForm):
    group_instance = None  # We don't care what the user inputs, we only are interested in the preset development_project_instance.

    def __init__(self, *args, **kwargs):
        # Restrict project field to the actual project this layer will belong to. This must
        # be popped off before the super is called:
        group_pk = kwargs.pop('group_pk', None)
        super(HeritageGISLayerForm, self).__init__(*args, **kwargs)

        if group_pk is not None:
            self.fields['group'].queryset = LayerGroup.objects.filter(pk=group_pk)
            self.fields['group'].initial = LayerGroup.objects.get(pk=group_pk)
            self.group_instance = self.fields['group'].initial  # save for later clean_project method

    # Double check that the project is what it is supposed to be.
    def clean_group(self):
        data = self.cleaned_data['group']
        if data != self.group_instance:
            raise forms.ValidationError("Dataset must be set to:",
                                        str(self.group_instance))
        return data

    # This little ditty here overrides the form superclass fields
    # and adds in the project.
    class Meta(GISLayerForm.Meta):
        model = HeritageGISLayer
        fields = GISLayerForm.Meta.fields + ('group',)


# Asset forms
class HeritageAssetForm(SecureAssetForm):
    class Meta:
        model = HeritageAsset
        fields = SecureAssetForm.Meta.fields


class ProjectAssetForm(SecureAssetForm):
    heritage_project_instance = None  # We don't care what the user inputs, we only are interested in the preset heritage_project_instance.

    def __init__(self, *args, **kwgargs):
        # Restrict project field to the actual project this layer will belong to. This must
        # be popped off before the super is called:
        h_project_id = kwgargs.pop('h_project_id', None)
        if h_project_id is None:
            raise TypeError('h_project_id is a required kwarg of ProjectAssetForm')

        super(ProjectAssetForm, self).__init__(*args, **kwgargs)

        self.fields['project'].queryset = Project.objects.filter(id=h_project_id)
        self.fields['project'].initial = Project.objects.get(id=h_project_id)
        self.heritage_project_instance = self.fields['project'].initial  # save for later clean_project method

    # Double check that the project is what it is supposed to be.
    def clean_project(self):
        data = self.cleaned_data['project']
        if data != self.heritage_project_instance:
            raise forms.ValidationError("Heritage Project must be set to:", str(self.heritage_project_instance))
        return data

    class Meta(SecureAssetForm.Meta):
        model = ProjectAsset
        fields = SecureAssetForm.Meta.fields + ('project',)


class InterviewAssetForm(SecureAssetForm):
    heritage_interview_instance = None  # We don't care what the user inputs, we only are interested in the preset heritage_interview_instance.

    def __init__(self, *args, **kwgargs):
        # Restrict interview field to the actual interview this layer will belong to. This must
        # be popped off before the super is called:
        h_interview_id = kwgargs.pop('h_interview_id', None)
        if h_interview_id is None:
            raise TypeError('h_interview_id is a required kwarg of InterviewAssetForm')

        super(InterviewAssetForm, self).__init__(*args, **kwgargs)

        self.fields['interview'].queryset = Interview.objects.filter(id=h_interview_id)
        self.fields['interview'].initial = Interview.objects.get(id=h_interview_id)
        self.heritage_interview_instance = self.fields['interview'].initial  # save for later clean_interview method

    # Double check that the interview is what it is supposed to be.
    def clean_interview(self):
        data = self.cleaned_data['interview']
        if data != self.heritage_interview_instance:
            raise forms.ValidationError("Heritage Interview must be set to:", str(self.heritage_interview_instance))
        return data

    class Meta(SecureAssetForm.Meta):
        model = InterviewAsset
        fields = SecureAssetForm.Meta.fields + ('interview',)


class PlaceForm(forms.ModelForm):
    class Meta:
        model = Place
        fields = ('name', 'add_to_community_map', 'notes', 'geometry', 'gazetteer_names', 'place_types')
        widgets = {
            'geometry': LeafletWidget(),
            'gazetteer_names': TagAutoSuggestSelect2(tagmodel='heritage.GazetteerNameTag', attrs={'startText': " "})
        }

class PlaceNameForm(forms.ModelForm):
    class Meta:
        model = None
        fields = '__all__'

class AlternatePlaceNameForm(PlaceNameForm):
    class Meta(PlaceNameForm.Meta):
        model = AlternatePlaceName


class CommonPlaceNameForm(PlaceNameForm):
    class Meta(PlaceNameForm.Meta):
        model = CommonPlaceName
