from datetime import datetime
from django import forms
from mptt.forms import TreeNodeChoiceField

from .models import EcosystemsAsset, EcosystemsProjectAsset, EcosystemsGISLayer, EcosystemsProject, FilingCode, \
    PlantTag, AnimalTag, CommonPlantName, IndigenousPlantName, CommonAnimalName, IndigenousAnimalName

from assets.forms import SecureAssetForm

from geoinfo.forms import GISLayerForm

from cedar_settings.models import GeneralSetting
from cedar_settings.utils.parsers import parse_choices


class EcosystemsAssetForm(SecureAssetForm):
    class Meta:
        model = EcosystemsAsset
        fields = SecureAssetForm.Meta.fields


class EcosystemsProjectAssetForm(SecureAssetForm):
    ecosystems_project_instance = None  # We don't care what the user inputs, we only are interested in the preset ecosystems_project_instance.

    def __init__(self, *args, **kwgargs):
        # Restrict project field to the actual project this layer will belong to. This must
        # be popped off before the super is called:
        eco_project_id = kwgargs.pop('eco_project_id', None)
        if eco_project_id is None:
            raise TypeError('eco_project_id is a required kwarg of EcosystemsProjectAssetForm')

        super(EcosystemsProjectAssetForm, self).__init__(*args, **kwgargs)

        self.fields['project'].queryset = EcosystemsProject.objects.filter(id=eco_project_id)
        self.fields['project'].initial = EcosystemsProject.objects.get(id=eco_project_id)
        self.ecosystems_project_instance = self.fields['project'].initial  # save for later clean_project method

    # Double check that the project is what it is supposed to be.
    def clean_project(self):
        data = self.cleaned_data['project']
        if data != self.ecosystems_project_instance:
            raise forms.ValidationError("Ecosystems Project must be set to:", str(self.ecosystems_project_instance))
        return data

    class Meta(SecureAssetForm.Meta):
        model = EcosystemsProjectAsset
        fields = SecureAssetForm.Meta.fields + ('project',)


class EcosystemsGISLayerForm(GISLayerForm):
    class Meta(GISLayerForm.Meta):
        model = EcosystemsGISLayer
    #     fields = GISLayerForm.Meta.fields + some_other_field


class EcosystemsProjectGISLayerForm(GISLayerForm):
    '''
    Small note: this form requires that a eco project is given when the form
    is instantiated, hides that input on the form, and validates against it.
    '''

    ecosystems_project_instance = None  # We don't care what the user inputs, we only are interested in the preset ecosystems_project_instance.

    def __init__(self, *args, **kwargs):
        # Restrict project field to the actual project this layer will belong to. This must
        # be popped off before the super is called:
        eco_project_id = kwargs.pop('eco_project_id', None)
        super(EcosystemsProjectGISLayerForm, self).__init__(*args, **kwargs)

        if eco_project_id is not None:
            self.fields['project'].queryset = EcosystemsProject.objects.filter(id=eco_project_id)
            self.fields['project'].initial = EcosystemsProject.objects.get(id=eco_project_id)
            self.ecosystems_project_instance = self.fields['project'].initial  # save for later clean_project method

            # If this form is creating a NEW gis layer, grab the ecosystems project code and prepopulate the
            # layer name with that:
            eco_gis_layer = kwargs.pop('instance', None)
            if eco_gis_layer is None:
                self.fields['name'].initial = EcosystemsGISLayer.suggest_layer_name(self.ecosystems_project_instance)

    # Double check that the project is what it is supposed to be.
    def clean_project(self):
        data = self.cleaned_data['project']
        if data != self.ecosystems_project_instance:
            raise forms.ValidationError("Ecosystems Project must be set to:", str(self.ecosystems_project_instance))
        return data

    # This little ditty here overrides the form superclass fields
    # and adds in the project.
    class Meta(GISLayerForm.Meta):
        model = EcosystemsGISLayer
        fields = GISLayerForm.Meta.fields + ('project',)


class EcosystemsProjectForm(forms.ModelForm):
    filing_code = TreeNodeChoiceField(queryset=FilingCode.objects.all())

    def __init__(self, *args, **kwargs):
        super(EcosystemsProjectForm, self).__init__(*args, **kwargs)

        # Parse the ecosystems_project_misc_textareas setting and create multiple text areas
        textarea_names = parse_choices(GeneralSetting.objects.get('ecosystems_project_misc_textareas'), False)

        for name in textarea_names:
            if name and name[0] and name[1]:
                self.fields["misc_textarea_%s" % name[0]] = forms.CharField(label=name[1],
                                                                            widget=forms.Textarea, required=False)

    def save(self, commit=True):
        obj = super(EcosystemsProjectForm, self).save(commit=commit)

        hstore_dict = obj.misc_textareas

        textarea_names = parse_choices(GeneralSetting.objects.get('ecosystems_project_misc_textareas'), False)
        for name in textarea_names:
            if name and name[0] and name[1]:
                field_name = "misc_textarea_%s" % name[0]
                hstore_dict[name[1]] = self.cleaned_data[field_name]

        obj.misc_textareas = hstore_dict

        if commit:
            obj.save()
        return obj

    class Meta:
        model = EcosystemsProject
        fields = '__all__'


class PlantTagForm(forms.ModelForm):
    """
    For editing the collection tag description field. Could be used for adding/removing linked Items.
    """
    def __init__(self, *args, **kwargs):
        super(PlantTagForm, self).__init__(*args, **kwargs)
        self.fields['slug'].required = False

    class Meta:
        model = PlantTag
        fields = '__all__'

    def save(self, commit=True):
        instance = super(PlantTagForm, self).save(commit=False)
        instance.slug = instance.slugify(instance.name)
        if commit:
            instance.save()
        return instance


class AnimalTagForm(forms.ModelForm):
    """
    For editing the collection tag description field. Could be used for adding/removing linked Items.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['slug'].required = False

    class Meta:
        model = AnimalTag
        fields = '__all__'

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.slug = instance.slugify(instance.name)
        if commit:
            instance.save()
        return instance


class AlternateSpeciesNameForm(forms.ModelForm):
    class Meta:
        model = None
        fields = '__all__'


class CommonPlantNameForm(AlternateSpeciesNameForm):
    class Meta(AlternateSpeciesNameForm.Meta):
        model = CommonPlantName


class IndigenousPlantNameForm(AlternateSpeciesNameForm):
    class Meta(AlternateSpeciesNameForm.Meta):
        model = IndigenousPlantName


class CommonAnimalNameForm(AlternateSpeciesNameForm):
    class Meta(AlternateSpeciesNameForm.Meta):
        model = CommonAnimalName


class IndigenousAnimalNameForm(AlternateSpeciesNameForm):
    class Meta(AlternateSpeciesNameForm.Meta):
        model = IndigenousAnimalName
