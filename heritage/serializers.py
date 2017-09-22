from django.db.models.functions import Lower
from rest_framework import serializers
from rest_framework.reverse import reverse
from rest_framework_gis.serializers import GeoFeatureModelSerializer, GeometryField
from easy_thumbnails.files import get_thumbnailer
import json

from .models import Species, SpeciesGroup, MTKSpeciesRecord, Use, TimeFrame, HarvestMethod, FishingMethod, \
    EcologicalValue, TemporalTrend, SpeciesTheme, Project, Interview, Session, InterviewAsset, SessionAsset, \
    ProjectAsset, MTKCulturalRecord, Feature, FeatureGroup, Group, TravelMode, HeritageAsset, HeritageGISLayer, \
    LayerGroup, Place

from crm.models import Person
from crm.serializers import PersonSerializer

from geoinfo.models import GISFeature
from geoinfo.serializers import GISLayerSerializer, GISFeatureGeoJSONSerializer, GISFeatureSerializer

from assets.serializers import AssetTypeSerializer, SecureAssetSerializer

from sanitizer.utils.sanitizer import sanitize


class FeatureGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeatureGroup


class FeatureSerializer(serializers.ModelSerializer):
    feature_group = FeatureGroupSerializer()

    class Meta:
        model = Feature


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group


class TravelModeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TravelMode


class SpeciesGroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = SpeciesGroup


# Serializers define the API representation.
class SpeciesSerializer(serializers.HyperlinkedModelSerializer):
    species_group = SpeciesGroupSerializer()

    class Meta:
        model = Species
        fields = ('description', 'other_detail', 'species_group', 'name_equivalents', 'id')


class UseSerializer(serializers.ModelSerializer):

    class Meta:
        model = Use


class TimeFrameSerializer(serializers.ModelSerializer):

    class Meta:
        model = TimeFrame


class HarvestMethodSerializer(serializers.ModelSerializer):

    class Meta:
        model = HarvestMethod


class FishingMethodSerializer(serializers.ModelSerializer):

    class Meta:
        model = FishingMethod


class EcologicalValueSerializer(serializers.ModelSerializer):

    class Meta:
        model = EcologicalValue


class TemporalTrendSerializer(serializers.ModelSerializer):

    class Meta:
        model = TemporalTrend


class SpeciesThemeSerializer(serializers.ModelSerializer):

    class Meta:
        model = SpeciesTheme


class SessionSerializer(serializers.ModelSerializer):
    # phase = ProjectSerializer()
    # interview = InterviewSerializer()
    participant_number = serializers.CharField(source='interview.participant_number')

    class Meta:
        model = Session


class InterviewSerializer(serializers.ModelSerializer):
    # phase = ProjectSerializer()
    phase_code = serializers.CharField(source='phase.phase_code')
    project_name = serializers.CharField(source='phase.name')
    # sessions = SessionSerializer(many=True, source='session_set')
    session_count = serializers.IntegerField(source='session_set.count')
    primary_interviewer = PersonSerializer()
    interview_number_string = serializers.CharField()
    url_api = serializers.HyperlinkedIdentityField(view_name="heritage:api:interview-detail")
    url_page = serializers.HyperlinkedIdentityField(view_name="heritage:interview-detail")
    participants = PersonSerializer(many=True)
    # lookup_field = "id"

    class Meta:
        model = Interview


# Use this to speed up the load of the interview list page:
class InterviewSerializerSlim(serializers.ModelSerializer):
    phase_code = serializers.CharField(source='phase.phase_code')
    project_name = serializers.CharField(source='phase.name')
    session_count = serializers.IntegerField(source='session_set.count')
    primary_interviewer = serializers.CharField(source='primary_interviewer.initials')
    interview_number_string = serializers.CharField()
    url_api = serializers.HyperlinkedIdentityField(view_name="heritage:api:interview-detail")
    url_page = serializers.HyperlinkedIdentityField(view_name="heritage:interview-detail")

    # participants = PersonSerializer(many=True)
    # lookup_field = "id"

    class Meta:
        model = Interview


class SpeciesObservationSerializer(serializers.HyperlinkedModelSerializer):
    species = SpeciesSerializer()
    use = UseSerializer()
    time_frame_start = TimeFrameSerializer()
    time_frame_end = TimeFrameSerializer()
    harvest_method = HarvestMethodSerializer()
    fishing_method = FishingMethodSerializer()
    ecological_value = EcologicalValueSerializer()
    temporal_trend = TemporalTrendSerializer()
    species_theme = SpeciesThemeSerializer()
    interview_id = serializers.IntegerField(source='interview.id')
    geom = serializers.SerializerMethodField()
    seasons = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = MTKSpeciesRecord
        fields = ('url', 'id', 'link_code', 'use', 'time_frame_start', 'time_frame_end', 'harvest_method', 'species',
                  'fishing_method', 'ecological_value', 'temporal_trend', 'species_theme', 'interview_id',
                  'gazetted_place_name', 'first_nations_place_name', 'local_place_name', 'seasons', 'participant_community', 'geom')
        extra_kwargs = {
            "url": {'view_name': 'heritage:species-observation-detail'}
        }

        # def get_interview_id(self, species_observation):
        #     return species_observation.interview.id

    # TODO: Fix api serialization of geojson. Right now it serializes and decodes,
    # only to have to serialize AGAIN before being sent out to the ViewSet.
    # This is so DUMB totally needs redoing....but it works.
    def get_geom(self, species_obs):
        children_qs = MTKSpeciesRecord.objects.select_subclasses().filter(pk=species_obs.id)
        the_json = children_qs.first().geometry.geojson
        d = json.JSONDecoder()
        return d.decode(the_json)


class CulturalObservationSerializer(serializers.HyperlinkedModelSerializer):
    # gazetted_place_name = serializers.CharField()
    # first_nations_place_name = serializers.CharField()
    ecological_feature = serializers.CharField(source='ecological_feature.description')
    cultural_feature = serializers.CharField(source='cultural_feature.description')
    industrial_feature = serializers.CharField(source='industrial_feature.description')
    management_feature = serializers.CharField(source='management_feature.description')
    value_feature = serializers.StringRelatedField()
    travel_mode = serializers.StringRelatedField()
    target_species = serializers.StringRelatedField()
    secondary_species = serializers.StringRelatedField()
    seasons = serializers.StringRelatedField(many=True, read_only=True)
    use = UseSerializer()
    time_frame_start = TimeFrameSerializer()
    time_frame_end = TimeFrameSerializer()
    # comments = serializers.CharField()
    interview_id = serializers.IntegerField(source='interview.id')
    geom = serializers.SerializerMethodField()

    class Meta:
        model = MTKSpeciesRecord
        fields = ('url', 'id', 'link_code', 'gazetted_place_name', 'first_nations_place_name', 'local_place_name', 'ecological_feature',
                  'cultural_feature', 'industrial_feature', 'management_feature', 'value_feature', 'travel_mode',
                  'target_species', 'secondary_species', 'seasons', 'use', 'time_frame_start', 'time_frame_end',
                  'participant_community', 'comments', 'interview_id', 'geom')
        extra_kwargs = {
            "url": {'view_name': 'heritage:cultural-observation-detail'}
        }

    # TODO: Fix api serialization of geojson. Right now it serializes and decodes,
    # only to have to serialize AGAIN before being sent out to the ViewSet.
    # This is so DUMB totally needs redoing....but it works.
    def get_geom(self, cultural_obs):
        children_qs = MTKCulturalRecord.objects.select_subclasses().filter(pk=cultural_obs.id)
        the_json = children_qs.first().geometry.geojson
        d = json.JSONDecoder()
        return d.decode(the_json)


class InterviewAssetSerializer(SecureAssetSerializer):
    delete_url = serializers.SerializerMethodField()

    class Meta(SecureAssetSerializer.Meta):
        model = InterviewAsset

    def get_delete_url(self, obj):
        return reverse('heritage:interview-secureasset-delete', kwargs={'interview_pk': obj.interview.id, 'pk': obj.id})

    def get_url(self, instance):
        return reverse('heritage:interview-secureasset-detail',
                       kwargs={'pk': instance.pk, 'interview_pk': instance.interview.pk})


class InterviewAssetSanitizedSerializer(InterviewAssetSerializer):
    name = serializers.SerializerMethodField()

    class Meta(SecureAssetSerializer.Meta):
        model = InterviewAsset

    def get_name(self, obj):
        return sanitize(obj.name, obj=obj.interview)


class SessionAssetSerializer(SecureAssetSerializer):
    session_num = serializers.SerializerMethodField()
    delete_url = serializers.SerializerMethodField()

    class Meta(SecureAssetSerializer.Meta):
        model = SessionAsset

    def get_session_num(self, instance):
        return instance.session.number

    def get_delete_url(self, obj):
        return reverse('heritage:session-secureasset-delete', kwargs={'session_pk': obj.session.id, 'pk': obj.id})


class SessionAssetSanitizedSerializer(SessionAssetSerializer):
    name = serializers.SerializerMethodField()

    class Meta(SessionAssetSerializer.Meta):
        model = SessionAsset

    def get_session_num(self, instance):
        return instance.session.number

    def get_name(self, obj):
        return sanitize(obj.name, obj=obj.session.interview)


class ProjectAssetSerializer(SecureAssetSerializer):
    class Meta(SecureAssetSerializer.Meta):
        model = ProjectAsset

    def get_url(self, instance):
        return reverse('heritage:project-secureasset-detail',
                       kwargs={'pk': instance.pk, 'project_pk': instance.project.pk})


class ProjectSerializer(serializers.ModelSerializer):
    interview_count = serializers.IntegerField(source='interview_set.count')
    participant_count = serializers.SerializerMethodField()
    document_count = serializers.SerializerMethodField()
    project_url = serializers.SerializerMethodField()
    picture_url = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = ('id', 'interview_count', 'participant_count', 'document_count', 'project_url', 'name', 'phase_code',
                  'year_string', 'start_date', 'end_date', 'location', 'background', 'picture_url', 'cedar_project_code')

    # Check out the sweet "|" operator - would be better to
    # just to a proper query, please do that.
    def get_participant_count(self, project):
        unique_set = Person.objects.none()

        for i in project.interview_set.all():
            unique_set = unique_set | i.participants.filter()

        return unique_set.count()

    def get_document_count(self, project):
        return ProjectAsset.objects.filter(project=project).count() \
               + InterviewAsset.objects.filter(interview__phase=project).count() \
               + SessionAsset.objects.filter(session__interview__phase=project).count()

    def get_project_url(self, project):
        return reverse('heritage:project-detail', args=[project.id, ])

    def get_picture_url(self, project):
        if project.picture:
            return get_thumbnailer(project.picture)['card'].url
        else:
            default_image_url = "/static/heritage/img/trees_700-500.jpg"
            return default_image_url


class ProjectDeepInfoSerializer(serializers.ModelSerializer):
    interview = InterviewSerializer(many=True, source='interview_set')
    # session = SessionSerializer(source='session')
    # participants = serializers.SerializerMethodField()


    class Meta:
        model = Project
        # depth = 1

    # def get_participants(self, project):
    #     # unique_set = Person.objects.none()
    #
    #     # for i in project.interview_set.all():
    #     #     unique_set = unique_set | i.participants.filter()
    #
    #     unique_set = Person.objects.all()
    #     serialized = PersonSerializer(many=True, data=unique_set)
    #     return serialized


class LayerGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = LayerGroup


class HeritageGISLayerSerializer(GISLayerSerializer):
    group = LayerGroupSerializer()

    class Meta:
        model = HeritageGISLayer
        fields = GISLayerSerializer.Meta.fields + ['group']


class HeritageGISLayerRelatedField(serializers.RelatedField):
    def to_representation(self, value):
        try:
            obj = HeritageGISLayer.objects.get(pk=value.pk)
            serializer = HeritageGISLayerSerializer(obj)
            return serializer.data
        except HeritageGISLayer.DoesNotExist:
            return None  # Bad form... but we only care about Features related to groups/interviews here....


class HeritageGISLayerFeatureGeoJSONSerializer(GISFeatureGeoJSONSerializer):
    # overrides layer field defined in super serializer.
    layer = HeritageGISLayerRelatedField(read_only=True)


class HeritageGISLayerFeatureSerializer(GISFeatureSerializer):
    layer = HeritageGISLayerRelatedField(read_only=True)


class HeritageGISLayerFeatureLazyGeoJSONSerializer(GISFeatureSerializer):
    layer = HeritageGISLayerRelatedField(read_only=True)
    geom = serializers.SerializerMethodField()

    class Meta(GISFeatureSerializer.Meta):
        fields = GISFeatureSerializer.Meta.fields + ('geom',)

    def get_geom(self, obj):
        feature = GISFeature.objects.get_subclass(pk=obj.pk)
        d = json.JSONDecoder()
        return d.decode(feature.geometry.json)


class PlaceSerializerWithGeoJSON(serializers.ModelSerializer):
    """
    Serializes Places WITH geometry fields formatted as geojson.
    """
    gazetteer_names = serializers.StringRelatedField(many=True)
    alternate_names = serializers.StringRelatedField(many=True, source='alternateplacename_set')
    common_names = serializers.StringRelatedField(many=True, source='commonplacename_set')
    place_types = serializers.StringRelatedField(many=True)
    geometry = serializers.SerializerMethodField()
    map_style = serializers.SerializerMethodField()

    class Meta:
        model = Place
        fields = ('id', 'prefixed_id', 'url', 'name', 'notes', 'alternate_names', 'common_names', 'gazetteer_names', 'place_types',
                  'geometry', 'map_style')
        extra_kwargs = {
            'url': {'view_name': 'heritage:place-detail'}
        }

    def get_geometry(self, obj):
        d = json.JSONDecoder()
        return d.decode(obj.geometry.geojson)

    def get_map_style(self, obj):
        try:
            return json.loads(obj.map_style.json)
        except AttributeError as e:
            return None


class PlaceGeoJSONSerializer(GeoFeatureModelSerializer):
    """
    Serializes places AS geojson.
    """
    gazetteer_names = serializers.StringRelatedField(many=True)
    alternate_names = serializers.StringRelatedField(many=True, source='alternateplacename_set')
    common_names = serializers.StringRelatedField(many=True, source='commonplacename_set')
    place_types = serializers.StringRelatedField(many=True)
    map_style = serializers.SerializerMethodField()

    class Meta:
        model = Place
        fields = ('id', 'prefixed_id', 'url', 'name', 'notes', 'alternate_names', 'common_names', 'gazetteer_names', 'place_types',
                  'geometry', 'map_style')
        geo_field = 'geometry'
        extra_kwargs = {
            'url': {'view_name': 'heritage:place-detail'}
        }

    def get_map_style(self, obj):
        try:
            return json.loads(obj.map_style.json)  # stupid hack
        except AttributeError as e:
            return None
