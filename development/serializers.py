from rest_framework import serializers
from rest_framework.reverse import reverse
from django.core.serializers.xml_serializer import Serializer as django_xml_serializer
from django.conf import settings
from django.utils.xmlutils import SimplerXMLGenerator

from .models import DevelopmentProject, DevelopmentGISLayer

from geoinfo.models import GISFeature
from geoinfo.serializers import GISLayerSerializer, GISFeatureGeoJSONSerializer


# from crm.models import Person
# from crm.serializers import PersonSerializer

class DevelopmentProjectSerializer(serializers.ModelSerializer):
    consultation_stage = serializers.StringRelatedField()
    filing_code = serializers.StringRelatedField()
    company = serializers.StringRelatedField()
    tags = serializers.StringRelatedField(many=True)
    url = serializers.SerializerMethodField()
    file_numbers = serializers.StringRelatedField(many=True, source='fileno_set')
    num_files = serializers.IntegerField(source='developmentprojectasset_set.count')
    num_comms = serializers.IntegerField(source='comm_relationships.count')
    num_comments = serializers.IntegerField(source='comments.count')

    class Meta:
        model = DevelopmentProject
        fields = ('id', 'cedar_project_name', 'cedar_project_code', 'consultation_stage', 'tags', 'url',
                  'initial_date', 'due_date', 'status', 'file_numbers', 'filing_code', 'company', 'num_files',
                  'num_comms', 'num_comments')

    def get_url(self, project):
        return reverse('development:project-detail', args=[project.id, ])


class DevelopmentGISLayerSerializer(GISLayerSerializer):

    class Meta:
        model = DevelopmentGISLayer
        fields = GISLayerSerializer.Meta.fields + ['project']


# A custom serializer to cast GISLayer into DevelopmentGISLayer
class DevelopmentGISLayerRelatedField(serializers.RelatedField):

    def to_representation(self, value):
        try:
            obj = DevelopmentGISLayer.objects.get(id=value.id)
            serializer = DevelopmentGISLayerSerializer(obj)
            return serializer.data
        except DevelopmentGISLayer.DoesNotExist:
            return None  # Bad form... but we only care about Features related to projects here....


class DevelopmentGISLayerFeatureGeoJSONSerializer(GISFeatureGeoJSONSerializer):
    # overrides layer field defined in super serializer.
    layer = DevelopmentGISLayerRelatedField(read_only=True)


class SERSerializer(django_xml_serializer):
    """
    Shared Engagement Record Serializer (SER)
    Slightly customized django core xml serializer. Changes the starting
    node element name to "cedar-objects" and sets version to C8 version number.
    """
    def start_serialization(self):
        """
        Start serialization -- open the XML document and the root element.
        """
        self.xml = SimplerXMLGenerator(self.stream, self.options.get("encoding", settings.DEFAULT_CHARSET))
        self.xml.startDocument()

        # TODO: get Cedar version from somewhere, not hard-coded here.
        self.xml.startElement("cedar-objects", {"version": "8.0"})

    def end_serialization(self):
        """
        End serialization -- end the document.
        """
        self.indent(0)
        self.xml.endElement("cedar-objects")
        self.xml.endDocument()
