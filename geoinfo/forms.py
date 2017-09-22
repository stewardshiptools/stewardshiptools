# from django.forms import ModelForm
from django.conf import settings
from django.contrib.gis import forms
from django.contrib.gis.geos import GEOSGeometry
from django.forms import ValidationError
from django.contrib.auth.models import User
from django.contrib.gis.forms.widgets import OSMWidget

from djcelery.models import IntervalSchedule, PeriodicTask

from .models import GISLayerMaster, GISLayer, SpatialReport, SpatialReportItem


class GISLayerMasterChoiceFieldLabelMixin(object):
    """
    Overrides the regular gis layer selector labels so we can see the app/type prefixes on layers.
    I would much rather NOT hard code the model types (eg developmentgislyaer, ecosystemsgislayer, etc.). Please
    find a better way.
    """
    def label_from_instance(self, obj):
        try:
            return str(obj.developmentgislayer)
        except obj.DoesNotExist:
            pass
        try:
            return str(obj.ecosystemsgislayer)
        except obj.DoesNotExist:
            pass
        try:
            return str(obj.heritagegislayer)
        except obj.DoesNotExist:
            pass
        return str(obj)


class GISLayerMasterModelChoiceField(GISLayerMasterChoiceFieldLabelMixin, forms.ModelChoiceField):
    """
    Use this field on a layer select field form where you want to see the layer name prefixed with the DEV, HER, ECO stuff.
    """
    pass


class GISLayerMasterModelMultipleChoiceField(GISLayerMasterChoiceFieldLabelMixin, forms.ModelMultipleChoiceField):
    """
    Use this field on a layer multi-select field form where you want to see the layer name prefixed with the DEV, HER, ECO stuff.
    """
    pass


# The default widget don't work!
class GeoinfoOSMWidget(OSMWidget):
    template_name = 'geoinfo/geoinfo-openlayers-osm.html'


class GISLayerForm(forms.ModelForm):
    """
    The top-level GIS layer form. Should be used by other apps for their
    own GIS layer stuff - Development, GISLayerAdmin.
    When subclassing, see https://docs.djangoproject.com/en/1.8/topics/forms/modelforms/#form-inheritance
    """

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(GISLayerForm, self).__init__(*args, **kwargs)
        self.user_instance = user

        default_interval = None
        obj = kwargs.get('instance', None)
        if obj is not None:
            try:
                ptask = PeriodicTask.objects.get(task="geoinfo.tasks.reload_layer_features", args=str([obj.pk]))
                default_interval = ptask.interval
            except PeriodicTask.DoesNotExist:
                pass

        self.fields['refresh_interval'] = forms.ModelChoiceField(
            required=False,
            queryset=IntervalSchedule.objects.all(),
            initial=default_interval,
            empty_label="Never"
        )

    def save(self, commit=True):
        obj = super(GISLayerForm, self).save(commit=False)

        if not obj.author:
            obj.author = self.user_instance

        try:
            # Identify any periodic tasks that refer to this layer...  There should only be one, or none.
            ptask = PeriodicTask.objects.get(task="geoinfo.tasks.reload_layer_features", args=str([obj.pk]))

            # A task exists... lets just attempt to update it.
            if self.cleaned_data['refresh_interval']:
                # Lets only update the task if the interval field has changed.
                # We get the initial directly from the field because we put it there.  It won't be in the modelform
                if self.fields['refresh_interval'].initial != self.cleaned_data['refresh_interval']:
                    ptask.interval = self.cleaned_data['refresh_interval']
                    ptask.save()

            else:
                ptask.delete()
        except PeriodicTask.DoesNotExist:
            # No task exists, lets create one!
            if self.cleaned_data['refresh_interval']:
                PeriodicTask.objects.create(
                    name="Update features for gislayer: {}".format(str(obj)),
                    task="geoinfo.tasks.reload_layer_features",
                    interval=self.cleaned_data['refresh_interval'],
                    args=str([obj.pk])
                )

        if commit:
            obj.save()

        return obj

    def clean_wkt(self):
        wkt = self.cleaned_data['wkt']
        try:
            g = GEOSGeometry(wkt)
            return wkt
        except ValueError as err:
            # raise forms.ValidationError("Invalid well-known-text.")
            return None

    def clean_wfs_password(self):
        pw = self.cleaned_data['wfs_password']
        if self.instance and self.instance.wfs_password and not pw:
            return self.instance.wfs_password
        return pw

    # Add validation for input type:
    def clean(self):
        cleaned_data = super(GISLayerForm, self).clean()
        input_type = cleaned_data.get('input_type')

        if input_type == 'wkt':
            if cleaned_data.get('wkt', None) is None:
                self.add_error('input_type', "Valid well-known-text is required if input type \"WKT\" is selected.")
                self.add_error('wkt', "Invalid well-known-text.")
                # raise forms.ValidationError("Valid well-known-text is required if input type \"WKT\" is selected.")

        # TODO Actually validate shapefile input.
        if input_type == 'file':
            if cleaned_data.get('file', None) is None:
                self.add_error('input_type', "A valid shapefile is required if input type \"file\" is selected.")
                self.add_error('file', "Invalid file.")
                # raise forms.ValidationError("A valid shapefile is required if input type \"file\" is selected.")

        # TODO Actually validate draw input.
        if input_type == 'map':
            if cleaned_data.get('draw', None) is None:
                self.add_error('input_type', "A valid shape is required on the map if input type \"draw on map\" is selected.")
                self.add_error('draw', "Invalid map drawing. ")
                # raise forms.ValidationError("A valid shape is required on the map if input type \"draw on map\" is selected.")

        return cleaned_data

    class Meta:
        model = GISLayer

        # We need to be explicit about which fields we want so that they can
        # be added to by any GISLayerForm subclasses. __all__ messed that up.
        fields = (
            'name',
            'input_type',
            'wkt',
            'draw',
            'feature_titles_template',
            'file',
            'geomark',
            'wfs_geojson',
            'wfs_username',
            'wfs_password',
            'notes',
            'author',
            'reload_features',
            'polygon_style',
            'polyline_style',
            'point_style'
        )

        widgets = {
            'draw': GeoinfoOSMWidget(attrs={
                'default_lon': getattr(settings, 'OPENLAYERS_DRAW_ON_MAP_LON', -126),
                'default_lat': getattr(settings, 'OPENLAYERS_DRAW_ON_MAP_LAT', 54.9),
                'default_zoom': getattr(settings, 'OPENLAYERS_DRAW_ON_MAP_ZOOM', 4)
            }),
            'wfs_password': forms.PasswordInput()
        }


# This is just a straight inheritance from the GISLayerForm to preserve
# other code and provides a place for further admin-page mods.
class GISLayerAdminForm(GISLayerForm):
    pass


class SpatialReportForm(forms.ModelForm):
    report_on = GISLayerMasterModelMultipleChoiceField(queryset=GISLayerMaster.objects.all())

    class Meta:
        model = SpatialReport
        fields = (
            'name',
            'distance_cap',
            'report_on'
        )


class SpatialReportItemForm(forms.ModelForm):
    layer = GISLayerMasterModelChoiceField(queryset=GISLayerMaster.objects.all())

    def __init__(self, *args, **kwargs):
        spatialreport_id = kwargs.pop('report_id', None)
        if spatialreport_id is None:
            raise TypeError('report_id is a required kwarg of SpatialReportItemForm')

        super(SpatialReportItemForm, self).__init__(*args, **kwargs)

        self.fields['report'].queryset = SpatialReport.objects.filter(id=spatialreport_id)
        self.fields['report'].initial = SpatialReport.objects.get(id=spatialreport_id)
        self.spatialreport_instance = self.fields['report'].initial

    def clean_report(self):
        data = self.cleaned_data['report']
        if data != self.spatialreport_instance:
            raise forms.ValidationError("Spatial Report must be set to:", str(self.spatialreport_instance))
        return data

    class Meta:
        model = SpatialReportItem
        fields = (
            'report',
            'distance_cap',
            'layer'
        )


class GeneralSpatialReportForm(forms.Form):
    name = forms.CharField(required=True)
    distance_cap = forms.CharField(required=True, help_text=SpatialReport._meta.get_field('distance_cap').help_text)
    layers = forms.MultipleChoiceField(choices=[], required=False)

    def __init__(self, *args, **kwargs):
        super(GeneralSpatialReportForm, self).__init__(*args, **kwargs)
        self.fields['layers'].choices = self.get_item_choices()

    def get_item_choices(self):
        return [(x.pk, str(x)) for x in GISLayer.objects.all()]
