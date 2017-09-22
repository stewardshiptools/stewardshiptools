from rest_framework import serializers
from rest_framework.reverse import reverse

from django.conf import settings

from .models import EcosystemsProject, ProjectTag, EcosystemsGISLayer, PlantTag, PlantTaggedItem, AnimalTag, AnimalTaggedItem

from geoinfo.serializers import GISLayerSerializer, GISFeatureGeoJSONSerializer
from geoinfo.models import GISFeature


class ProjectTagSerializer(serializers.ModelSerializer):
    tag = serializers.CharField()

    class Meta:
        model = ProjectTag


class EcosystemsProjectSerializer(serializers.ModelSerializer):
    tags = ProjectTagSerializer(many=True)
    url = serializers.SerializerMethodField()

    class Meta:
        model = EcosystemsProject
        fields = ('id', 'cedar_project_name', 'cedar_project_code', 'tags',
                  'url', 'start_date', 'end_date')

    def get_url(self, project):
        return reverse('ecosystems:project-detail', args=[project.id, ])


class EcosystemsGISLayerSerializer(GISLayerSerializer):
    class Meta:
        model = EcosystemsGISLayer
        fields = GISLayerSerializer.Meta.fields + ['project']


# A custom serializer to cast GISLayer into EcosystemsGISLayer
class EcosystemsGISLayerRelatedField(serializers.RelatedField):

    def to_representation(self, value):
        try:
            obj = EcosystemsGISLayer.objects.get(id=value.id)
            serializer = EcosystemsGISLayerSerializer(obj)
            return serializer.data
        except EcosystemsGISLayer.DoesNotExist:
            return None  # Bad form... but we only care about Features related to projects here....


class EcosystemsGISLayerFeatureGeoJSONSerializer(GISFeatureGeoJSONSerializer):
    # overrides layer field defined in super serializer.
    layer = EcosystemsGISLayerRelatedField(read_only=True)


class PlantTagSerializer(serializers.HyperlinkedModelSerializer):
    items_count = serializers.SerializerMethodField()

    def get_items_count(self, obj):
        return PlantTaggedItem.objects.filter(tag=obj).count()

    class Meta:
        model = PlantTag
        fields = ('description', 'name', 'items_count', 'url')
        extra_kwargs = {
            "url": {'view_name': 'ecosystems:planttag-detail'}
        }


class AnimalTagSerializer(serializers.HyperlinkedModelSerializer):
    items_count = serializers.SerializerMethodField()

    def get_items_count(self, obj):
        return AnimalTaggedItem.objects.filter(tag=obj).count()

    class Meta:
        model = AnimalTag
        fields = ('description', 'name', 'items_count', 'url')
        extra_kwargs = {
            "url": {'view_name': 'ecosystems:animaltag-detail'}
        }