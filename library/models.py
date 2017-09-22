import uuid
from django.db.models import Q, F, Value, CharField
from django.db.models.functions import Concat
from django.contrib.gis.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

from cedar.models import PrefixedIDModelAbstract

from crm.models import UserPersonProxy

from model_utils.models import TimeStampedModel
from django_hstore.fields import DictionaryField
from mptt.models import MPTTModel, TreeForeignKey

from heritage.models import Place
from security.models import SecurityLevel

from taggit.managers import TaggableManager
from taggit.models import TagBase, TaggedItemBase, ItemBase, GenericTaggedItemBase

from assets.models import SecureAsset
from tags.models import TaggedItem
from tags.managers import TaggableManagerExtended


class LibraryObject(PrefixedIDModelAbstract, models.Model):
    """
    Abstract model that defines some properties that will be common to any 
     object stored in the library app.
     
     The easiest way to set this value when working with forms is to set a kwarg in the urls.py
      of the app you are working in with you include the library urls (see dev, her, eco for examples). 
      You can then just kwargs.get('belongs_to') in the views that you need that value.
    """

    belongs_to = models.CharField(max_length=100, blank=True, null=True, verbose_name='App that this object belongs to')

    class Meta:
        abstract = True


class GenericReferenceMixin(object):
    obj_ct = models.ForeignKey(ContentType, blank=True, null=True, on_delete=models.CASCADE)
    obj_id = models.PositiveIntegerField(blank=True, null=True)
    obj = GenericForeignKey('related_object_ct', 'related_object_id')


class LibraryTagRequestMixin(models.Model):
    """
    Mix this in to a custom tag that has a belongs_to attribute.
    Then use the TaggitAutoSuggestExtended for the form field widget.
    It will let taggit autosuggest filter the tags based on the belongs_to
    field.
    """
    @staticmethod
    def request_filter(request):
        """
        Used by taggit autosuggest to filter the tags returned by a get request.
        :param request: 
        :return: 
        """
        if request.method == 'GET':
            belongs_to = request.GET.get('belongs_to', None)
        elif request.method == 'POST':
            belongs_to = request.POST.get('belongs_to', None)
        else:
            belongs_to = None

        if belongs_to:
            return models.Q(belongs_to=belongs_to)
        else:
            return models.Q()

    class Meta:
        abstract = True


#########################
# Items                 #
#########################


class ItemType(MPTTModel):
    """
    Defines the type of library Item.
    Is referred to by the DublicCore model therefore to access an Item's type:
        Item.dublin_core.type.name
    """
    name = models.CharField(max_length=250)
    description = models.TextField(blank=True, null=True)

    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', db_index=True)

    def __str__(self):
        return self.name


class Item(LibraryObject, TimeStampedModel):
    """
    The main model of the Library.
    Items relate to files (via ItemRelation) and point to other metadata models as req'd. Dublin Core
    is mandatory.
    """
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)

    name = models.CharField(max_length=500)

    dublin_core = models.OneToOneField('DublinCore')
    holdings = models.OneToOneField('Holdings', blank=True, null=True, on_delete=models.SET_NULL)
    review = models.OneToOneField('Review', blank=True, null=True, on_delete=models.SET_NULL)
    researcher_notes = models.OneToOneField('ResearcherNotes', blank=True, null=True, on_delete=models.SET_NULL)
    confidentiality = models.OneToOneField('Confidentiality', blank=True, null=True, on_delete=models.SET_NULL)

    # Relations
    # TODO project (This was a field called heritage project in MIL.  There was only ever one.
    # Could this now be a heritage.Project? or a Tag?
    cataloger = models.ForeignKey(UserPersonProxy, blank=True, null=True, related_name="%(app_label)s_%(class)s_cataloger_related", on_delete=models.SET_NULL)
    reviewer = models.ForeignKey(UserPersonProxy, blank=True, null=True, related_name="%(app_label)s_%(class)s_reviewer_related", on_delete=models.SET_NULL)

    files = models.ManyToManyField(SecureAsset, through='ItemAssetRelation', through_fields=('item', 'secureasset',), blank=True)

    # Related items
    related_items = models.ManyToManyField('Item', blank=True, symmetrical=True)

    extra_data = DictionaryField(blank=True, null=True)

    tags = TaggableManager(through=TaggedItem, blank=True)
    collections = TaggableManager(through='CollectionTaggedItem', blank=True)

    def __str__(self):
        return self.name

    @classmethod
    def get_prefix(cls):
        return "I-"

    def get_absolute_url(self):
        return reverse("library:item-detail", kwargs={'pk': self.pk})


class ItemRelatedObjects(GenericReferenceMixin, models.Model):
    item = models.ForeignKey('Item', related_name='related_objects', on_delete=models.CASCADE)


class ItemAssetRelation(models.Model):
    """
    Relates an Item to an asset via a generic relation.
    """
    item = models.ForeignKey('Item')
    secureasset = models.ForeignKey(SecureAsset)

    # This generic relation should only point to SecureAssets and Assets
    # content_type = models.ForeignKey(ContentType)
    # object_id = models.PositiveIntegerField()
    # asset = GenericForeignKey('content_type', 'object_id')


class Category(models.Model):
    """
    NEEDS DOCSTRING
    """
    name = models.CharField(max_length=250)
    weight = models.SmallIntegerField(default=0)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class MUPCategory(Category):
    """
    NEEDS DOCSTRING
    """

    class Meta:
        verbose_name_plural = 'MUP Categories'


class UseAndOccupancyCategory(Category):
    """
    NEEDS DOCSTRING
    """

    class Meta:
        verbose_name_plural = 'Use and Occupancy Categories'


class GenericMetadataAbstract(LibraryObject, models.Model):
    """
    Abstract Metadata base class.
    Just a placeholder for now, use if you
    need to add a field or method to child classes.
    """
    class Meta:
        abstract = True


class DublinCore(GenericMetadataAbstract):
    """
    Dublin Core Metadata model. Referred to by Item (OneToOne) and is a required field.
    Implements the Dublin Core Metadata Element Set, Version 1.1.
    See http://dublincore.org/documents/2008/01/14/dces/
    See https://github.com/aleray/django-dcdocuments/blob/master/dcdocuments/models.py
    """

    # Stubbed in for fun.
    # meta_types = {
    #     '1': {
    #         'type_name': 'audio_file',
    #         'fields': ['contributor', 'coverage']
    #     }
    # }

    help_texts = {
        'contributor': 'An entity responsible for making contributions to the resource.',
        'coverage': 'The spatial or temporal topic of the resource, the spatial applicability \
                           of the resource, or the jurisdiction under which the resource is relevant.',
        'creator': 'I.e. Author, Format: Last Name, First Name - Title;',
        'date': 'A point or period of time associated with an event in the lifecycle of the resource.',
        'description': 'An account of the resource.',
        'format': 'The file format, physical medium, or dimensions of the resource.',
        'identifier': 'An unambiguous reference to the resource within a given context.',
        'language': 'A language of the resource.',
        'publisher': 'An entity responsible for making the resource available.',
        'relation': 'A related resource.',
        'rights': 'Information about rights held in and over the resource.',
        'source': 'A related resource from which the described resource is derived.',
        'subject': 'The topic of the resource.',
        'type': 'The nature or genre of the resource.',
        'external_identifier': 'Publisher and Source data should follow the standard format used in the Chicago Manual of Style. Archival'
                               ' or record source information should also be included in this field as follows: Place: Name of Archive or '
                               'Institution, Section (if known), Archival Collection Number, Volume Number, Folio or File Number; Microfilm '
                               'Number. For example: Victoria, B.C.: Royal Columbia Museum, Anthropological Collections Section, MS. 421, '
                               'Vol. 11, f. 4; Microfilm 267'
    }

    contributor = models.TextField(blank=True, null=True, verbose_name='Contributors', help_text=help_texts['contributor'])
    coverage = models.TextField(blank=True, null=True, verbose_name='Coverage', help_text=help_texts['coverage'])
    creator = models.TextField(blank=True, null=True, verbose_name='Author/Creator', help_text=help_texts['creator'])
    date = models.DateField(blank=True, null=True, verbose_name='Date', help_text=help_texts['date'])
    description = models.TextField(blank=True, null=True, verbose_name='Description', help_text=help_texts['description'])
    format = models.TextField(blank=True, null=True, verbose_name='Format', help_text=help_texts['format'])
    identifier = models.TextField(blank=True, null=True, verbose_name='Identifier', help_text=help_texts['identifier'])
    language = models.TextField(blank=True, null=True, verbose_name='Language', help_text=help_texts['language'])
    publisher = models.TextField(blank=True, null=True, verbose_name='Publishers', help_text=help_texts['publisher'])
    relation = models.TextField(blank=True, null=True, verbose_name='Relation', help_text=help_texts['relation'])
    rights = models.TextField(blank=True, null=True, verbose_name='Rights', help_text=help_texts['rights'])
    source = models.TextField(blank=True, null=True, verbose_name='Source', help_text=help_texts['source'])
    subject = models.TextField(blank=True, null=True, verbose_name='Subject', help_text=help_texts['subject'])

    type = models.ForeignKey('ItemType', blank=True, null=True)

    external_identifier = models.TextField(blank=True, null=True, verbose_name='External Identifier',  help_text=help_texts['external_identifier'])

    def get_absolute_url(self):
        from django.core.urlresolvers import reverse_lazy
        return reverse_lazy('library:item-detail', args=[self.item.id])

    def __str__(self):
        try:
            return '{} ({})'.format(str(self.item), self.item.prefixed_id)
        except Item.DoesNotExist:
            return 'Dublin Core {}.'.format(self.id)


class Holdings(GenericMetadataAbstract):
    """
    Holdings metadata model. Referred to OneToOne by Item
    """
    help_texts = {
        'source_type': 'Primary Source - A document or record containing first-hand information '
                       'or original data on a topic; A work created at the time of an event or by '
                       'a person who directly experienced an event; Some examples include: interviews, '
                       'diaries, letters, journals, original hand-written manuscripts, newspaper and '
                       'magazine clippings, government documents, etc. Secondary Source - Any published '
                       'or unpublished work that is one step removed from the original source, usually '
                       'describing, summarizing, analyzing, evaluating, derived from, or based on '
                       'primary source materials; A source that is one step removed from the original '
                       'event or experience; A source that provides criticism or interpretation of a '
                       'primary source; Some examples include: textbooks, review articles, biographies, '
                       'historical films, music and art, articles about people and events from the past.',

        'media_mode': "Is the document a Physical (paper hardcopy) or Digital (scanned as PDF, "
                      "Word Doc, Jpg, etc) or Both (you have it in its original state and "
                      "as a digital file).",

        'digital_file_name_path': "Enter the full file name and path for the document, for "
                                  "example if the file is stored on a shared drive. Example "
                                  "S://heritage/2010/project/documents/file_123_20100213.pdf",

        'dimensions': "If the Item is a physical object, add  "
                                  "dimensions. Example 10 cm x 20 cm x 3 cm",

    }

    source_type_choices = [
        ('Primary', 'Primary'),
        ('Secondary', 'Secondary')
    ]

    media_mode_choices = [
        ('Physical', 'Physical'),
        ('Digital', 'Digital'),
        ('Both', 'Both')
    ]

    # Type, location, and files
    item_type_comments = models.TextField(blank=True, null=True, help_text='The Item Type is selected in the Identification')
    source_type = models.CharField(max_length=250, blank=True, null=True, choices=source_type_choices,
                                   help_text=help_texts['source_type'])
    media_mode = models.CharField(max_length=250, blank=True, null=True, choices=media_mode_choices,
                                  help_text=help_texts['media_mode'])
    item_internal_location = models.TextField(blank=True, null=True)
    digital_file_name_path = models.CharField(max_length=500, blank=True, null=True,
                                              help_text=help_texts['digital_file_name_path'])
    digital_file_name = models.CharField(max_length=2000, blank=True, null=True)
    digital_file_ocrd = models.BooleanField(default=False)

    # Dropped digital_file_type in favour of Item type.  Not sure if we need the comments.
    digital_file_type_comments = models.TextField(blank=True, null=True)

    dimensions = models.CharField(max_length=250, blank=True, null=True, help_text=help_texts['dimensions'])

    class Meta:
        verbose_name_plural = 'Holdings'

    def get_absolute_url(self):
        from django.core.urlresolvers import reverse_lazy
        return reverse_lazy('library:item-detail', args=[self.item.id])

    def __str__(self):
        try:
            return '{} ({})'.format(str(self.item), self.item.prefixed_id)
        except Item.DoesNotExist:
            return 'Holding {}.'.format(self.id)


class Review(models.Model):
    """
    Review metadata model. Referred to by Item (one2one)
    """
    # Review
    summary = models.TextField(blank=True, null=True)

    # TODO Places Mentioned (Gazateer, searchable) - Not sure what to do about this.
    places_mentioned = models.ManyToManyField(Place, blank=True, related_name='item_reviews')

    plants = TaggableManager(through='ecosystems.PlantTaggedItem', blank=True)
    animals = TaggableManager(through='ecosystems.AnimalTaggedItem', blank=True)

    people_mentioned = TaggableManager(through='PersonMentionedTaggedItem', blank=True, related_name='people_mentioned_tags')

    mup_category = models.ManyToManyField('MUPCategory', blank=True)
    use_occupancy_category = models.ManyToManyField('UseAndOccupancyCategory', blank=True)
    full_text = models.TextField(blank=True, null=True)

    def __str__(self):
        try:
            return '{} ({})'.format(str(self.item), self.item.prefixed_id)
        except Item.DoesNotExist:
            return 'Review {}.'.format(self.id)

    def get_absolute_url(self):
        from django.core.urlresolvers import reverse_lazy
        return reverse_lazy('library:item-detail', args=[self.item.id])


class ResearcherNotes(GenericMetadataAbstract):
    """
    Reseacher metadata model. Referred to OneToOne by Item
    """
    spreadsheet_id = models.PositiveIntegerField(blank=True, null=True)
    researcher_notes = models.TextField(blank=True, null=True)
    actions_needed = models.TextField(blank=True, null=True)
    search_location = models.CharField(max_length=500, blank=True, null=True)
    search_terms = models.CharField(max_length=500, blank=True, null=True)
    search_results = models.CharField(max_length=500, blank=True, null=True)
    search_identifier = models.CharField(max_length=500, blank=True, null=True)
    cross_reference = models.CharField(max_length=500, blank=True, null=True)
    search_summary = models.TextField(blank=True, null=True)

    def __str__(self):
        try:
            return '{} ({})'.format(str(self.item), self.item.prefixed_id)
        except Item.DoesNotExist:
            return 'Researcher Notes {}'.format(self.id)

    def get_absolute_url(self):
        from django.core.urlresolvers import reverse_lazy
        return reverse_lazy('library:item-detail', args=[self.item.id])


class Confidentiality(models.Model):
    """
    Item security model.

    Greg thinks we should drop this for a global access control system.
    """
    # TODO Delete the confidential field after migrating its values into the new security level system.
    confidential = models.BooleanField('Confidential', default=True)

    comments = models.TextField(blank=True, null=True)
    release_signed = models.BooleanField(default=False)

    def __str__(self):
        try:
            return '{} ({})'.format(str(self.item), self.item.prefixed_id)
        except Item.DoesNotExist:
            return 'Confidentiality {}'.format(self.id)

    def get_absolute_url(self):
        from django.core.urlresolvers import reverse_lazy
        return reverse_lazy('library:item-detail', args=[self.item.id])


############################
# Collections              #
############################
class CollectionTag(LibraryObject, LibraryTagRequestMixin, TagBase):
    """ A custom tag model to provide a description field to Collection Tags.
    """
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Collection Tag"
        verbose_name_plural = "Collection Tags"


class CollectionTaggedItem(ItemBase):
    """
    Acts as the through model from Item <-> CollectionTag relationship
    It inherits from ItemBase and creates its own version of taggit.TaggedItemBase
        - TaggedItemBase.tag was not permitting me to use a custom tag model (CollectionTag).
    """
    tag = models.ForeignKey(CollectionTag, related_name="%(app_label)s_%(class)s_items", on_delete=models.CASCADE)
    content_object = models.ForeignKey('Item')

    @classmethod
    def tags_for(cls, model, instance=None, **extra_filters):
        """
        This is a ripoff of taggit.TaggedItemBase.tags_for()
        I don't know where this is used, if at all, but I am re-creating the taggit.TaggedItemBase
        class here and this was the only thing left to do besides re-creating the tag model field. 
        :param model: 
        :param instance: 
        :param extra_filters: 
        :return: 
        """
        kwargs = extra_filters or {}
        if instance is not None:
            kwargs.update({
                '%s__content_object' % cls.tag_relname(): instance
            })
            return cls.tag_model().objects.filter(**kwargs)
        kwargs.update({
            '%s__content_object__isnull' % cls.tag_relname(): False
        })
        return cls.tag_model().objects.filter(**kwargs).distinct()


#############################
# Case Briefs               #
#############################
class CaseBrief(LibraryObject, TimeStampedModel):
    reasons_choices = (
        ('said', 'Said'),
        ('unsaid', 'Unsaid')
    )

    uuid = models.UUIDField(default=uuid.uuid4, editable=False)

    story_title = models.CharField(max_length=500, blank=True, null=True)
    cataloger = models.ForeignKey(UserPersonProxy, blank=True, null=True,
                                  related_name="%(app_label)s_%(class)s_cataloger_related", on_delete=models.SET_NULL)
    reviewer = models.ForeignKey(UserPersonProxy, blank=True, null=True,
                                 related_name="%(app_label)s_%(class)s_reviewer_related", on_delete=models.SET_NULL)
    sources = models.ManyToManyField('Item', blank=True, verbose_name="Source(s)",
                                     help_text='Select the library item(s) containing the digital version of the story cited.')
    source_notes = models.TextField(blank=True, null=True, verbose_name="Source Notes",
                                    help_text='Notes describing where in the documents the story can be found.')
    issues = models.TextField(blank=True, null=True, help_text='The main issue(s) or problem(s) that the story focuses on.')
    facts = models.TextField(blank=True, null=True,
                             help_text='Facts in the story that are relevant to understanding the issue(s) and their resolution. '
                                       'Who, What, When and Where? Use point form.')
    decision = models.TextField(blank=True, null=True, verbose_name='Decision / Resolution',
                                help_text='Describe what is decided or how the issue is finally addressed or resolved')

    reasons_notes = models.TextField(blank=True, null=True, verbose_name='Reason(s)',
                                     help_text='Describe the background to the Resolution using these categories: '
                                               'Said - A reason behind the decision or resolution that is stated or explained in the story; '
                                               'Unsaid - A reason behind the decision or resolution that is not directly stated or explained '
                                               'in the story, but that you interpret as a reason or explanation.')

    notes = models.TextField(blank=True, null=True,
                             help_text='General notes. Include anything that provides greater context to the story '
                                       'e.g. words, songs, dances, art, place names, etc. Include unanswered questions that require follow up.')

    tags = TaggableManager(through=TaggedItem, blank=True)
    keywords = TaggableManagerExtended(through='CaseBriefTaggedItem', blank=True,
                                       help_text='Words, names, places, etc. that you think should be highlighted.'
                                       # belongs_to='heritage-library'
                                       )

    def __str__(self):
        return "{}".format(self.story_title)

    @classmethod
    def get_prefix(cls):
        return "CB-"

    def get_absolute_url(self):
        from django.core.urlresolvers import reverse_lazy
        return reverse_lazy('library:casebrief-detail', args=[self.id])


class CaseBriefRelatedObjects(GenericReferenceMixin, models.Model):
    casebrief = models.ForeignKey('CaseBrief', related_name='related_objects', on_delete=models.CASCADE)


class CaseBriefTag(LibraryObject, LibraryTagRequestMixin, TagBase):
    """ 
    Aka "Keywords". A custom tag model specific to Case Briefs.
    """
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Case Brief Tag"
        verbose_name_plural = "Case Brief Tags"


class CaseBriefTaggedItem(ItemBase):
    """
    Acts as the through model for CaseBrief <-> CaseBriefTag relationship
    """
    tag = models.ForeignKey(CaseBriefTag, related_name="%(app_label)s_%(class)s_items", on_delete=models.CASCADE)
    content_object = models.ForeignKey('CaseBrief')

    @classmethod
    def tags_for(cls, model, instance=None, **extra_filters):
        """
        This is a ripoff of taggit.TaggedItemBase.tags_for()
        I don't know where this is used, if at all, but I am re-creating the taggit.TaggedItemBase
        class here and this was the only thing left to do besides re-creating the tag model field. 
        :param model: 
        :param instance: 
        :param extra_filters: 
        :return: 
        """
        kwargs = extra_filters or {}
        if instance is not None:
            kwargs.update({
                '%s__content_object' % cls.tag_relname(): instance
            })
            return cls.tag_model().objects.filter(**kwargs)
        kwargs.update({
            '%s__content_object__isnull' % cls.tag_relname(): False
        })
        return cls.tag_model().objects.filter(**kwargs).distinct()


##################################################
# Synthesis                                      #
##################################################
class Synthesis (LibraryObject, TimeStampedModel):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)

    name = models.CharField(max_length=500, blank=False, null=False)

    class Meta:
        verbose_name_plural = "Syntheses"

    def __str__(self):
        return 'Synthesis {}. {}'.format(self.id, self.name)

    def get_absolute_url(self):
        from django.core.urlresolvers import reverse_lazy
        return reverse_lazy('library:synthesis-detail', args=[self.id])

    @classmethod
    def get_prefix(cls):
        return "SY-"


class SynthesisRelatedObjects(GenericReferenceMixin, models.Model):
    synthesis = models.ForeignKey('Synthesis', related_name='related_objects', on_delete=models.CASCADE)


class SynthesisCategory (models.Model):
    name = models.CharField(max_length=500, blank=False, null=False)
    weight = models.IntegerField(default=0)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Synthesis Categories"


class SynthesisItem(LibraryObject, TimeStampedModel):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)

    subject = models.CharField(max_length=500, blank=False, null=False)
    overview = models.TextField(blank=True, null=True)
    items = models.ManyToManyField('Item', verbose_name="Item Sources", blank=True)
    casebriefs = models.ManyToManyField('CaseBrief', verbose_name="Case Brief Sources", blank=True)
    synthesis = models.ForeignKey(Synthesis)
    category = models.ForeignKey(SynthesisCategory, blank=True, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return "{} - Concept: {} ({})".format(self.synthesis.name, self.subject, self.synthesis.prefixed_id)

    class Meta:
        ordering = ('id',)

    def get_absolute_url(self):
        from django.core.urlresolvers import reverse_lazy
        return reverse_lazy('library:synthesisitem-detail', args=[self.synthesis.id, self.id])


class PersonMentionedTag(TagBase):
    """
    Add extra fields here if needed
    """
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Person Mentioned"
        verbose_name_plural = "People Mentioned"

    def get_absolute_url(self):
        from django.core.urlresolvers import reverse_lazy
        return reverse_lazy('library:personmentionedtag-detail', args=[self.id])


class PersonMentionedTaggedItem(GenericTaggedItemBase):
    tag = models.ForeignKey(PersonMentionedTag, related_name="%(app_label)s_%(class)s_items")
    note = models.TextField(blank=True, null=True)

