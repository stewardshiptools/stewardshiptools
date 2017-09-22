from django.contrib.contenttypes.models import ContentType

from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer as BaseGeoFeatureModelSerializer, GeometrySerializerMethodField, GeometryField

from .models import GISLayerMaster, GISLayer, GISFeature, GISFeaturePoint, GISFeatureLine, GISFeaturePolygon, SpatialReport,\
    SpatialReportItem


# from maps.serializers import StyleCircleModelSerializer, StylePolylineModelSerializer, StylePolygonModelSerializer
import maps


class GeoFeatureModelSerializer(BaseGeoFeatureModelSerializer):
    """
    Stub in to start diagnosing and fixing this serializer on geometry collection fields.
    """
    pass


class GISLayerSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    author = serializers.StringRelatedField()
    url = serializers.SerializerMethodField()
    feature_count = serializers.IntegerField(source='gisfeature_set.count')
    edit_url = serializers.SerializerMethodField()
    delete_url = serializers.SerializerMethodField()

    # remove time and timezone info from the created field for
    # display. If this impacts sorting and things then tough titty.
    created = serializers.DateTimeField(format="%Y-%m-%d")

    class Meta:
        model = GISLayer
        fields = ['id', 'name', 'url', 'feature_count', 'edit_url', 'delete_url', 'input_type', 'notes', 'author',
                  'created', 'modified']

    def get_name(self, obj):
        obj_sc = GISLayerMaster.objects.get_subclass(pk=obj.pk)
        return str(obj_sc)

    def get_url(self, obj):
        model = obj.__class__

        try:
            subclass = model.objects.get_subclass(pk=obj.pk)
            return subclass.get_absolute_url()
        except AttributeError:
            return obj.get_absolute_url()

    def get_edit_url(self, obj):
        model = obj.__class__

        try:
            subclass = model.objects.get_subclass(pk=obj.pk)
            return subclass.get_edit_url()
        except AttributeError:
            return obj.get_edit_url()

    def get_delete_url(self, obj):
        model = obj.__class__

        try:
            subclass = model.objects.get_subclass(pk=obj.pk)
            return subclass.get_delete_url()
        except AttributeError:
            return obj.get_delete_url()


class GISLayerSlimSerializer(GISLayerSerializer):
    '''
    used by the GISFeatureDistanceSerializer which is called up
    by spatial reports.
    only supply fields that are absolutely necessary. Seems to make
    a significant difference.
    '''
    class Meta:
        model = GISLayer
        fields = ['id', 'name', 'url',]


class GISLayerMasterSerializer(GISLayerSerializer):
    class Meta:
        model = GISLayerMaster
        fields = GISLayerSerializer.Meta.fields + ['layer_type']


class GISFeaturePointSerializer(serializers.ModelSerializer):
    class Meta:
        model = GISFeaturePoint


class GISFeatureLineSerializer(serializers.ModelSerializer):
    class Meta:
        model = GISFeatureLine


class GISFeaturePolygonSerializer(serializers.ModelSerializer):
    class Meta:
        model = GISFeaturePolygon


# A custom serializer to figure out which type of feature is being added and using the correct serializer.
# TODO I don't think this is being used... remove it?
class GISFeatureRelatedField(serializers.RelatedField):

    def to_representation(self, value):
        obj = GISFeature.objects.get_subclass(id=value.id)
        data = None

        if obj.__class__.__name__ == 'GISFeaturePoint':
            serializer = GISFeaturePointSerializer(obj)
            data = serializer.data
            data['type'] = 'Point'
        elif obj.__class__.__name__ == 'GISFeatureLine':
            serializer = GISFeatureLineSerializer(obj)
            data = serializer.data
            data['type'] = 'LineString'
        elif obj.__class__.__name__ == 'GISFeaturePolygon':
            serializer = GISFeaturePolygonSerializer(obj)
            data = serializer.data
            data['type'] = 'Polygon'

        return data


class GISFeatureStyleSerializerMixin(serializers.Serializer):
    """
    Not actually a mixin; wouldn't work if it only inherited from object.
    """
    map_style = serializers.SerializerMethodField()

    def get_map_style(self, obj):
        try:
            if hasattr(obj, 'gisfeatureline'):
                return obj.gisfeatureline.map_style.json
            elif hasattr(obj, 'gisfeaturepoint'):
                return obj.gisfeaturepoint.map_style.json
            elif hasattr(obj, 'gisfeaturepolygon'):
                return obj.gisfeaturepolygon.map_style.json
            else:
                return None
        except AttributeError as e:
            # the map style for the selected type is none. keep going
            return None


class GISFeatureGeoJSONSerializer(GISFeatureStyleSerializerMixin, GeoFeatureModelSerializer):
    '''
    Called up by GISFeatureViewSet which is used in pulling features for regular map drawing (others?).
    GISFeatureViewSet requires the as_geojson parameter in the url for this serializer to be used.
    '''
    geom = GeometryField(source='geom_simple')

    # layer = GISLayerSerializer()  # The map component uses this layer field to identify cedar map overlays.
    layer = GISLayerSlimSerializer()

    class Meta:
        model = GISFeature
        fields = ('id', 'url', 'name', 'layer', 'data', 'geom', 'map_style')
        geo_field = 'geom'
        extra_kwargs = {
            "url": {'view_name': 'geoinfo:feature-detail'}
        }


class GISFeatureSerializer(serializers.HyperlinkedModelSerializer):
    '''
    Called up by GISFeatureViewSet if the as_geojson paramter is NOT in the url.
    I presume this serializer is for listing GISFeature tabular data (eg List tab in layer deets),
    and therefore doesn't require spatial data (?).
    This should be called: "GISFeatureAttributeSerializer"
    '''
    layer = serializers.StringRelatedField()

    class Meta:
        model = GISFeature
        fields = ('id', 'url', 'name', 'layer', 'data')
        extra_kwargs = {
            "url": {'view_name': 'geoinfo:feature-detail'}
        }


class GISFeatureDistanceSerializer(serializers.HyperlinkedModelSerializer):
    '''
    Called up by GISFeatureShapeViewSet by default. Also subclassed by GISFeaturePointGeoJSONSerializer,
    GISFeatureLineGeoJSONSerializer, GISFeaturePolygonGeoJSONSerializer.
    '''
    layer = GISLayerSlimSerializer()

    # Since this is provided as an annotated field it will be visible but we do have
    # to tell the serializer that it exists since it isn't defined in the model.
    distance = serializers.SerializerMethodField()
    group = serializers.SerializerMethodField()
    sort_group = serializers.SerializerMethodField()

    class Meta:
        model = GISFeature
        fields = ('id', 'url', 'name', 'group', 'sort_group', 'distance', 'layer', 'data')
        extra_kwargs = {
            "url": {'view_name': 'geoinfo:feature-detail'}
        }

    def get_distance(self, obj):
        try:
            if obj.distance.m == 0:
                return {
                    'value': 'Intersecting',
                    'unit': ''
                }
            elif obj.distance.m > 1000:
                return {
                    'value': round(obj.distance.km, 4),
                    'unit': 'km'
                }
        except AttributeError:
            return {
                'value': obj.distance,
                'unit': ''
            }

        return {
            'value': round(obj.distance.m, 2),
            'unit': 'm'
        }

    def get_layer_url(self, obj):
        layer_model = obj.layer.__class__
        layer_subclass = layer_model.objects.get_subclass(id=obj.layer.id)
        return layer_subclass.get_absolute_url()

    def get_group(self, obj):
        layer = GISLayerMaster.objects.get_subclass(pk=obj.layer.pk)
        layer_ct = ContentType.objects.get_for_model(layer)

        return layer_ct.model_class()._meta.verbose_name.title()

    def get_sort_group(self, obj):
        layer = GISLayerMaster.objects.get_subclass(pk=obj.layer.pk)
        layer_ct = ContentType.objects.get_for_model(layer)

        try:
            if layer_ct.app_label == 'geoinfo' or not layer.project:
                return str(layer)
            else:
                return layer_ct.model_class()._meta.verbose_name.title()
        except AttributeError as e:
            return str(layer)


class GISFeaturePointGeoJSONSerializer(GeoFeatureModelSerializer, GISFeatureDistanceSerializer, GISFeatureStyleSerializerMixin):
    geom = GeometryField(source='geom_simple')
    map_style = serializers.SerializerMethodField()

    class Meta:
        model = GISFeaturePoint
        fields = ('id', 'url', 'name', 'layer', 'distance', 'data', 'geom', 'map_style')
        geo_field = 'geom'
        extra_kwargs = {
            "url": {'view_name': 'geoinfo:feature-detail'}
        }

    def to_representation(self, instance):
        return super().to_representation(instance)


class GISFeatureLineGeoJSONSerializer(GeoFeatureModelSerializer, GISFeatureDistanceSerializer, GISFeatureStyleSerializerMixin):
    geom = GeometryField(source='geom_simple')
    map_style = serializers.SerializerMethodField()

    class Meta:
        model = GISFeatureLine
        fields = ('id', 'url', 'name', 'layer', 'distance', 'data', 'geom', 'map_style')
        geo_field = 'geom'
        extra_kwargs = {
            "url": {'view_name': 'geoinfo:feature-detail'}
        }

    def to_representation(self, instance):
        return super().to_representation(instance)


class GISFeaturePolygonGeoJSONSerializer(GeoFeatureModelSerializer, GISFeatureDistanceSerializer, GISFeatureStyleSerializerMixin):
    geom = GeometryField(source='geom_simple')
    map_style = serializers.SerializerMethodField()

    class Meta:
        model = GISFeaturePolygon
        fields = ('id', 'url', 'name', 'layer', 'distance', 'data', 'geom', 'map_style')
        geo_field = 'geom'
        extra_kwargs = {
            "url": {'view_name': 'geoinfo:feature-detail'}
        }



class SpatialReportItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = SpatialReportItem
        fields = ('distance_cap', 'layer')


class SpatialReportSerializer(serializers.ModelSerializer):
    report_on = GISLayerSerializer(many=True)
    spatialreportitem_set = SpatialReportItemSerializer(many=True)

    class Meta:
        model = SpatialReport
        fields = ('id', 'url', 'name', 'distance_cap', 'report_on', 'spatialreportitem_set')
        extra_kwargs = {
            "url": {'view_name': 'geoinfo:spatialreport-detail'}
        }
