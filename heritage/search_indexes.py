import datetime
from haystack import indexes
from .models import HeritageAsset, Place

from assets.search_indexes import DocumentIndex

name_boost = 1.25


class HeritageAssetIndex(DocumentIndex, indexes.Indexable):
    def get_model(self):
            return HeritageAsset


class PlaceIndex(indexes.SearchIndex, indexes.Indexable):
    def get_model(self):
        return Place

    text = indexes.CharField(document=True, use_template=True)
    document_template_name = 'search/indexes/heritage/place_text.txt'

    name = indexes.CharField(null=False, model_attr='name', boost=name_boost)
    notes = indexes.CharField(null=True, model_attr='notes')
    prefixed_id = indexes.CharField(model_attr='prefixed_id')

    alternate_names = indexes.FacetMultiValueField()
    common_names = indexes.FacetMultiValueField()
    gazetteer_names = indexes.FacetMultiValueField()
    place_types = indexes.FacetMultiValueField()

    def index_queryset(self, using=None):
        '''
        Get the default QuerySet to index when doing a full update.
        Subclasses can override this method to avoid indexing certain objects.
        :param using:
        :return:
        '''
        qs = super().index_queryset(using=using)
        return qs

    def prepare_alternate_names(self, obj):
        return [place.name for place in obj.alternateplacename_set.all()]

    def prepare_common_names(self, obj):
        return [place.name for place in obj.commonplacename_set.all()]

    def prepare_gazetteer_names(self, obj):
        return [gaz.name for gaz in obj.gazetteer_names.all()]

    def prepare_place_types(self, obj):
        return [place_type.place_type for place_type in obj.place_types.all()]
