##############################################################################################
# assets
# todo: document asset model usage.
#   Briefly:
#       - subclass Asset or Secure asset for an asset in the app (eg Heritage).
#       - chain child asset models if you like: ProjectAsset
#                                                   InterviewAsset  (child of ProjectAsset)
#                                                       SessionAsset (child of InterviewAsset)
#       - An asset's physical storage location is determined by the storage_string property.
#           If you don't care where it goes you don't have to do anything. It will default to
#           the parent's implementation of the storage_location property.
#           If you do care you must override the parent storage_location property. Get the
#           parent's storage_location (by calling super) and append to it the subfolder where
#           you want your child to go.
##############################################################################################

from django.db import models
from django.utils import timezone

from django.core.urlresolvers import reverse

# from heritage.models import Project, Interview, Session
from . import asset_helpers

from model_utils.managers import InheritanceManagerMixin, InheritanceManager

from cedar_settings.models import GeneralSetting


# Not implemented. Bugs found:
# When assets are deleted with this object manager, and then try to delete with
# the "admin_objects" manager, inheritance pointers fail.
class PublishedAssetInheritanceObjectManager(InheritanceManagerMixin, models.Manager):
    def get_queryset(self):
        return super(PublishedAssetInheritanceObjectManager, self).get_queryset().filter(published=True)


class AssetType(models.Model):
    type_of_asset = models.CharField(max_length=30)
    description = models.CharField(max_length=150, blank=True, null=True)

    def __str__(self):
        return self.type_of_asset

    class Meta:
        ordering = ('type_of_asset',)


class AssetAbstract(models.Model):
    name = models.CharField(max_length=250, blank=False, null=False)
    asset_type = models.ForeignKey(AssetType, blank=True, null=True)
    delete_file_with_record = models.BooleanField(default=True, help_text='This will delete the file if this asset is deleted')
    comment = models.CharField(max_length=800, blank=True, null=True)
    published = models.BooleanField(default=True)

    legacy_path = models.CharField(max_length=2000, blank=True, null=True,
                                   help_text="This may hold a file path pointing to the original file location")

    # modified is updated in signals.py.
    modified = models.DateTimeField(blank=True, null=True, verbose_name="Date & time record modified.")

    # objects = PublishedAssetInheritanceObjectManager()
    objects = InheritanceManager()

    @property
    def file_size_str(self):
        try:
            return asset_helpers.sizeof_fmt(self.file.size)
        except (ValueError, FileNotFoundError) as err:
            return "0-DNE"

    @property
    def storage_string(self):
        '''
        This is what the filepath generator will use to create the storage path.
        It must be implemented in asset child classes.
        :return:
        '''
        return None

    @property
    def source_url(self):
        '''
        Should be overridden in children - used in search results pages.
        HeritageAsset has a good example.
        :return: url to instance that this object belongs to. "" if none.
        '''
        return ''

    @property
    def source_string(self):
        '''
        Should be overridden in children - used in search results pages to describe
        the linking object (DEV project, HER project, HER interview, etc)
        HeritageAsset has a good example.
        :return:
        '''
        return GeneralSetting.objects.get('assets__default_asset_source_string')

    @property
    def search_template(self):
        '''
        :return: path to default search result template.
        '''
        return 'search/results/asset_result.html'

    class Meta:
        abstract = True

    def __str__(self):

        if self.storage_string is not None:
            return self.name + ": " + self.storage_string
        else:
            return self.name


class Asset(AssetAbstract):
    file = models.FileField(upload_to=asset_helpers.generate_asset_file_name, max_length=255)

    # objects = InheritanceManager()

    def get_absolute_url(self):
        return reverse('assets:asset-detail', args=[self.id])

    @property
    def url(self):
        return self.get_absolute_url()

    @property
    def download_url(self):
        return reverse('assets:asset-download', args=[self.id])

    class Meta:
        ordering = ('-modified',)


class SecureAsset(AssetAbstract):
    """
    Note: If you try to get the url of the file itself django will
    try to build the url from the regular /media route, which will fail.
    See secure_file_storage in asset_helpers.py.
    To get a secure asset file's view/download url, reverse the urls:
        'secureasset-download' and 'secureasset-serve' in assets.urls.py
    """
    file = models.FileField(
            upload_to=asset_helpers.generate_asset_file_name,
            storage=asset_helpers.secure_file_storage,
            max_length=255)

    # objects = InheritanceManager()

    class Meta:
        permissions = (
            ("view_secureasset", "Can view secure asset"),
        )
        ordering = ('-modified',)

    def get_absolute_url(self):
        return reverse('assets:secureasset-detail', args=[self.id])

    @property
    def url(self):
        return self.get_absolute_url()

    @property
    def download_url(self):
        return reverse('assets:secureasset-download', args=[self.id])

    @property
    def serve_url(self):
        return reverse('assets:secureasset-serve', args=[self.id])

    @property
    def delete_url(self):
        return reverse('assets:secureasset-delete', args=[self.id])


class MetaDocumentAbstract(models.Model):
    """
    Abstract Meta Class.
    Subclass into Asset and SecureAsset.
    It implements the Dublin Core Metadata Element Set, Version 1.1.
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
        'creator': 'An entity primarily responsible for making the resource.',
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
        'title': 'A name given to the resource.',
        'type': 'The nature or genre of the resource.'
    }

    contributor = models.TextField(blank=True, null=True, verbose_name='Contributors', help_text=help_texts['contributor'])
    coverage = models.TextField(blank=True, null=True, verbose_name='Coverage', help_text=help_texts['coverage'])
    creator = models.TextField(blank=True, null=True, verbose_name='Creators', help_text=help_texts['creator'])
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
    title = models.TextField(blank=True, null=True, verbose_name='Title', help_text=help_texts['title'])
    type = models.TextField(blank=True, null=True, verbose_name='Type', help_text=help_texts['type'])

    def __str__(self):
        return 'id:{}. title: {}'.format(self.id, self.title)

    class Meta:
        abstract = True


class MetaDocumentSecureAsset(MetaDocumentAbstract):
    asset = models.OneToOneField(SecureAsset, related_name='meta_document', null=True)

    def __str__(self):
        return 'id:{}. asset: {}. title: {}'.format(self.id, self.asset.name, self.title)


class MetaDocumentAsset(MetaDocumentAbstract):
    asset = models.OneToOneField(Asset, related_name='meta_document', null=True)

    def __str__(self):
        return 'id:{}. asset: {}. title: {}'.format(self.id, self.asset.name, self.title)
