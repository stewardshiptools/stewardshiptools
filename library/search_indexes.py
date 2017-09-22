from haystack import indexes
from library.models import Item, CaseBrief, SynthesisItem, Synthesis, CollectionTag

name_boost = 1.25

class LibraryCommonIndexPropertiesMixin(object):
    belongs_to = indexes.CharField()


# class ItemIndex(indexes.SearchIndex): # this would disable indexing for this index class.
class ItemIndex(LibraryCommonIndexPropertiesMixin, indexes.SearchIndex, indexes.Indexable):

    '''
        Item Index - I originally hoped this would be a NON-indexed Index class which is then subclassed into 
        apps' index classes and made indexable there so facilitate restricting to app-level access. Not sure what the
        future holds for that concept though.

        For guidance:
        http://django-haystack.readthedocs.io/en/latest/best_practices.html#good-search-needs-good-content

        "indexes.Indexable" - tells django-haystack to index that material. Without
            it the index is ignored.

        Note on assets:
            - I think we can leave the secureasset index largely in place - BUT in the index_queryset
            method we should restrict the selection to secureassets that are part of Library ie: they have
            an entry in ItemAsset relation.

        Tags:
        http://django-haystack.readthedocs.io/en/v2.4.1/searchindex_api.html#prepare-self-object
    '''

    def get_model(self):
            return Item

    '''
    Item index document :
    '''
    text = indexes.CharField(document=True, use_template=True)
    document_template_name = 'search/indexes/library/item_text.txt'

    '''
    Item Fields
    '''
    name = indexes.CharField(null=False, model_attr='name', boost=name_boost)
    tags = indexes.FacetMultiValueField()
    collections = indexes.FacetMultiValueField()
    cataloger = indexes.CharField(model_attr='cataloger', null=True)
    reviewer = indexes.CharField(model_attr='reviewer', null=True)
    prefixed_id = indexes.CharField(model_attr='prefixed_id')
    file_names = indexes.FacetMultiValueField()

    '''
    DublinCore Fields
    '''
    item_type = indexes.FacetCharField(null=True, model_attr='dublin_core__type')
    contributor = indexes.FacetCharField(null=True, model_attr='dublin_core__contributor')
    coverage = indexes.FacetCharField(null=True, model_attr='dublin_core__coverage')
    creator = indexes.FacetCharField(null=True, model_attr='dublin_core__creator')
    date = indexes.FacetDateField(null=True, model_attr='dublin_core__date')
    description = indexes.CharField(null=True, model_attr='dublin_core__description')
    format = indexes.CharField(null=True, model_attr='dublin_core__format')
    identifier = indexes.CharField(null=True, model_attr='dublin_core__identifier')
    language = indexes.FacetCharField(null=True, model_attr='dublin_core__language')
    publisher = indexes.CharField(null=True, model_attr='dublin_core__publisher')
    relation = indexes.CharField(null=True, model_attr='dublin_core__relation')
    rights = indexes.CharField(null=True, model_attr='dublin_core__rights')
    source = indexes.CharField(null=True, model_attr='dublin_core__source')
    subject = indexes.CharField(null=True, model_attr='dublin_core__subject')

    '''
    Holdings Fields
    '''
    item_type_comments = indexes.CharField(null=True, model_attr='holdings__item_type_comments')
    source_type = indexes.FacetCharField(null=True, model_attr='holdings__source_type')
    media_mode = indexes.FacetCharField(null=True, model_attr='holdings__media_mode')
    item_internal_location = indexes.CharField(null=True, model_attr='holdings__item_internal_location')
    digital_file_name_path = indexes.CharField(null=True, model_attr='holdings__digital_file_name_path')
    digital_file_name = indexes.CharField(null=True, model_attr='holdings__digital_file_name')
    digital_file_ocrd = indexes.FacetBooleanField(null=True, model_attr='holdings__digital_file_ocrd')
    digital_file_type_comments = indexes.CharField(null=True, model_attr='holdings__digital_file_type_comments')

    '''
    Review Fields
    '''
    summary = indexes.CharField(null=True, model_attr='review__summary')
    people_mentioned = indexes.FacetMultiValueField()
    plants = indexes.FacetMultiValueField()
    animals = indexes.FacetMultiValueField()
    mup_category = indexes.FacetCharField(null=True, model_attr='review__mup_category__name')
    use_occupancy_category = indexes.FacetCharField(null=True, model_attr='review__use_occupancy_category__name')
    full_text = indexes.FacetCharField(null=True, model_attr='review__full_text')

    '''
    ResearcherNotes Fields
    '''
    spreadsheet_id = indexes.FacetIntegerField(null=True, model_attr='researcher_notes__spreadsheet_id')
    researcher_notes = indexes.CharField(null=True, model_attr='researcher_notes__researcher_notes')
    actions_needed = indexes.CharField(null=True, model_attr='researcher_notes__actions_needed')
    search_location = indexes.CharField(null=True, model_attr='researcher_notes__search_location')
    search_terms = indexes.FacetCharField(null=True, model_attr='researcher_notes__search_terms')
    search_results = indexes.CharField(null=True, model_attr='researcher_notes__search_results')
    search_identifier = indexes.FacetCharField(null=True, model_attr='researcher_notes__search_identifier')
    cross_reference = indexes.FacetCharField(null=True, model_attr='researcher_notes__cross_reference')
    search_summary = indexes.CharField(null=True, model_attr='researcher_notes__search_summary')

    def index_queryset(self, using=None):
        '''
        Get the default QuerySet to index when doing a full update.
        Subclasses can override this method to avoid indexing certain objects.
        :param using:
        :return:
        '''

        # the super does this:
        # self.get_model().objects.all()

        qs = super(ItemIndex, self).index_queryset(using=using)
        return qs

    def prepare_tags(self, obj):
        return [tag.name for tag in obj.tags.all()]

    def prepare_collections(self, obj):
        return [tag.name for tag in obj.collections.all()]

    def prepare_file_names(self, obj):
        return [file.name for file in obj.files.all()]

    def prepare_people_mentioned(self, obj):
        if obj.review:
            return [tag.name for tag in obj.review.people_mentioned.all()]
        else:
            return None

    def prepare_plants(self, obj):
        if obj.review:
            return [tag.name for tag in obj.review.plants.all()]
        else:
            return None

    def prepare_animals(self, obj):
        if obj.review:
            return [tag.name for tag in obj.review.animals.all()]
        else:
            return None


class CaseBriefIndex(LibraryCommonIndexPropertiesMixin, indexes.SearchIndex, indexes.Indexable):

    '''
        Case Brief Index:

        For guidance:
        http://django-haystack.readthedocs.io/en/latest/best_practices.html#good-search-needs-good-content

        Tags:
        http://django-haystack.readthedocs.io/en/v2.4.1/searchindex_api.html#prepare-self-object
    '''

    def get_model(self):
            return CaseBrief

    # Main document index:
    text = indexes.CharField(document=True, use_template=True)
    document_template_name = 'search/indexes/library/casebrief_text.txt'

    name = indexes.CharField(null=False, model_attr='story_title', boost=name_boost)  # use story title for boosted name field
    story_title = indexes.CharField(null=False, model_attr='story_title')
    cataloger = indexes.CharField(model_attr='cataloger', null=True)
    reviewer = indexes.CharField(model_attr='reviewer', null=True)
    prefixed_id = indexes.CharField(model_attr='prefixed_id')

    # sources =
    source_notes = indexes.CharField()
    issues = indexes.CharField()
    facts = indexes.CharField()
    decision = indexes.CharField()
    reasons = indexes.FacetCharField()
    notes = indexes.CharField()

    tags = indexes.FacetMultiValueField()
    keywords = indexes.FacetMultiValueField()


    def prepare_tags(self, obj):
        return [tag.name for tag in obj.tags.all()]

    def prepare_keywords(self, obj):
        return [keyword.name for keyword in obj.keywords.all()]


class SynthesisIndex(LibraryCommonIndexPropertiesMixin, indexes.SearchIndex, indexes.Indexable):

    '''
        Synthesis Index:
        
        For guidance:
        http://django-haystack.readthedocs.io/en/latest/best_practices.html#good-search-needs-good-content

    '''

    def get_model(self):
            return Synthesis

    # Main document index:
    text = indexes.CharField(document=True, use_template=True)
    document_template_name = 'search/indexes/library/synthesis_text.txt'
    prefixed_id = indexes.CharField(model_attr='prefixed_id')
    name = indexes.CharField(boost=name_boost)


class SynthesisItemIndex(LibraryCommonIndexPropertiesMixin, indexes.SearchIndex, indexes.Indexable):

    '''
        Synthesis Item Index:
        
        For guidance:
        http://django-haystack.readthedocs.io/en/latest/best_practices.html#good-search-needs-good-content

    '''

    def get_model(self):
            return SynthesisItem

    # Main document index:
    text = indexes.CharField(document=True, use_template=True)
    document_template_name = 'search/indexes/library/synthesisitem_text.txt'

    subject = indexes.CharField()
    overview = indexes.CharField()
    # items = indexes.CharField()
    # casebriefs = indexes.CharField()
    synthesis_category = indexes.CharField(model_attr='category__name', null=True)


class CollectionTagIndex(LibraryCommonIndexPropertiesMixin, indexes.SearchIndex, indexes.Indexable):

    '''
        Collection Tag Index:
        
        For guidance:
        http://django-haystack.readthedocs.io/en/latest/best_practices.html#good-search-needs-good-content

    '''

    def get_model(self):
            return CollectionTag

    # Main document index:
    text = indexes.CharField(document=True, use_template=True)
    document_template_name = 'search/indexes/library/collectiontag_text.txt'

    name = indexes.CharField(boost=name_boost)
    description = indexes.CharField()

