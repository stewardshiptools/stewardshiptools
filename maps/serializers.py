from rest_framework import serializers
from rest_framework.reverse import reverse

# from .models import LeafletMap, LeafletBaseLayer, LeafletTileLayer, LeafletOverlayLayer, LeafletOverlayGeoinfoLayer, \
#     StylePolygon, StylePolyline, StyleCircle, StyleMarker, CompositeStyle

import maps.models

from geoinfo.serializers import GISLayerMasterSerializer


# Use this boolean serializer if you want a 0 or a 1
# when the field is serialized. I used in a JS map setting
# that required a JS true or false (not string, not uppercase T or F).
# This might be put into the cedar app folder because it may have uses
# elsewhere.
class BinaryBooleanSerializerField(serializers.BooleanField):
    def to_representation(self, value):
        val = super(BinaryBooleanSerializerField, self).to_representation(value)
        if val:
            return 1
        else:
            return 0


class LeafletOverlayGeoinfoLayerSerializer(serializers.ModelSerializer):
    # geoinfo_layer = GISLayerMasterSerializer()
    url = serializers.SerializerMethodField()

    def get_url(self, obj):
        ajax_url = "{}?{}={}&as_geojson=1".format(reverse('geoinfo:api:feature-list'), 'layer', obj.geoinfo_layer.id)
        return ajax_url

    class Meta:
        model = maps.models.LeafletOverlayGeoinfoLayer


class LeafletOverlayLayerSerializer(serializers.ModelSerializer):

    class Meta:
        model = maps.models.LeafletOverlayLayer


# A custom serializer to figure out which type of Overlay Layer is being added and using the correct serializer.
class LeafletOverlayLayerRelatedField(serializers.RelatedField):

    def to_representation(self, value):
        obj = maps.models.LeafletOverlayLayer.objects.get_subclass(id=value.id)
        data = None

        if obj.__class__.__name__ == 'LeafletOverlayGeoinfoLayer':
            serializer = LeafletOverlayGeoinfoLayerSerializer(obj)
            data = serializer.data
            data['type'] = 'geoinfo-overlaylayer'
        elif obj.__class__.__name__ == 'LeafletBaseLayer':
            serializer = LeafletOverlayLayerSerializer(obj)
            data = serializer.data
            data['type'] = 'overlaylayer'

        return data


class LeafletBaseLayerSerializer(serializers.ModelSerializer):

    class Meta:
        model = maps.models.LeafletBaseLayer


class LeafletTileLayerSerializer(serializers.ModelSerializer):
    max_zoom = serializers.SerializerMethodField()

    class Meta:
        model = maps.models.LeafletTileLayer

    def get_max_zoom(self, obj):
        return obj.max_zoom or ''


# A custom serializer to figure out which type of Layer is being added and using the correct serializer.
class LeafletBaseLayerRelatedField(serializers.RelatedField):

    def to_representation(self, value):
        obj = maps.models.LeafletBaseLayer.objects.get_subclass(id=value.id)
        data = None

        if obj.__class__.__name__ == 'LeafletTileLayer':
            serializer = LeafletTileLayerSerializer(obj)
            data = serializer.data
            data['type'] = 'tile-layer'
        elif obj.__class__.__name__ == 'LeafletBaseLayer':
            serializer = LeafletBaseLayerSerializer(obj)
            data = serializer.data
            data['type'] = 'base-layer'

        return data


class LeafletMapSerializer(serializers.ModelSerializer):
    available_overlay_layers = LeafletOverlayLayerRelatedField(many=True, read_only=True)
    base_layers = LeafletBaseLayerRelatedField(many=True, read_only=True)
    default_base_layer = LeafletBaseLayerRelatedField(read_only=True)
    layer_control_collapsed = BinaryBooleanSerializerField()


    class Meta:
        model = maps.models.LeafletMap


class StylePathModelSerializerAbstract(serializers.ModelSerializer):
    """
    Serializes to a tidy leaflet compatible style.
    """
    stroke = serializers.BooleanField()


class StylePolygonModelSerializer(StylePathModelSerializerAbstract):
    """
    Serializes to a tidy leaflet compatible style.
    """
    fill = serializers.BooleanField()
    leaflet_layer_type = serializers.CharField()

    class Meta:
        model = maps.models.StylePolygon
        exclude = ('id', 'style_name')


class StylePolylineModelSerializer(StylePathModelSerializerAbstract):
    """
    Serializes to a tidy leaflet compatible style.
    """
    leaflet_layer_type = serializers.CharField()

    class Meta:
        model = maps.models.StylePolyline
        exclude = ('id', 'style_name')


class StyleCircleModelSerializer(StylePathModelSerializerAbstract):
    """
    Serializes to a tidy leaflet compatible style.
    """
    leaflet_layer_type = serializers.CharField()

    class Meta:
        model = maps.models.StyleCircle
        exclude = ('id', 'style_name', 'layer_type')


class StyleMarkerModelSerializer(serializers.ModelSerializer):
    """
    Serializes to a tidy leaflet compatible style.
    """
    leaflet_layer_type = serializers.CharField()
    square = BinaryBooleanSerializerField()
    icon = serializers.CharField(source='identifier')
    className = serializers.CharField()

    class Meta:
        model = maps.models.StyleMarker
        exclude = ('id', 'style_name', 'identifier',)


class CompositeStyleModelSerializer(serializers.ModelSerializer):
    """
    Serializes to a tidy leaflet compatible style.
    """
    polyline_style = StylePolylineModelSerializer()
    marker_style = StyleMarkerModelSerializer()
    composite = serializers.SerializerMethodField()

    class Meta:
        model = maps.models.CompositeStyle
        fields = ('polyline_style', 'marker_style', 'composite')

    def get_composite(self, obj):
        return 'true'
