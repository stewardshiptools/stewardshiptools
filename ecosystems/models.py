from django.core.urlresolvers import reverse
from django.contrib.gis.db import models
from django.db.models import Q, F, Value, CharField
from django.db.models.functions import Concat
from django.contrib.contenttypes.models import ContentType
from django_hstore.hstore import DictionaryField, HStoreGeoManager, HStoreManager
from model_utils.managers import InheritanceManager
from mptt.models import MPTTModel, TreeForeignKey
import psycopg2
from django.db import connection

from taggit.managers import TaggableManager
from taggit.models import TagBase, ItemBase, GenericTaggedItemBase, TaggedItemBase

from geoinfo.models import GISLayerMaster

import assets
from assets import asset_helpers

from crm.models import Person, Organization

from cedar_settings.models import GeneralSetting

from communication.models import HarvestCodePrefix


class EcosystemsProjectObjectManager(HStoreManager):
    def get_queryset(self):
        '''
        Override get_queryset to annotate objects with the cedar_project_code_q field
        :return:
        '''
        qs = super(EcosystemsProjectObjectManager, self).get_queryset()

        default_prefix_instance = EcosystemsProject.get_project_code_prefix()

        # A lame fix for the objects.get calls
        # In DevelopmentProject.get_projet_code_prefix() breaking hstore EVERYWHERE.....
        psycopg2.extras.register_hstore(connection.cursor(), globally=True)

        return qs.annotate(
            cedar_project_code_q=Concat(
                Value("{}".format(default_prefix_instance)),
                F('id'),
                output_field=CharField()
            )
        )


class EcosystemsProject(models.Model):
    status_choices = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    )

    cedar_project_name = models.CharField(max_length=250, blank=False, null=False)

    filing_code = TreeForeignKey('FilingCode', blank=True, null=True)

    tags = models.ManyToManyField('ProjectTag', blank=True)

    # Dates
    start_date = models.DateField('Project Start Date', blank=True, null=True)
    end_date = models.DateField('Project End Date', blank=True, null=True)

    author = models.ForeignKey(Person, related_name='author', blank=False, verbose_name='Author', on_delete=models.PROTECT)

    # CRM / Persons
    contacts = models.ManyToManyField(Person, related_name='contacts', blank=True, verbose_name='Contacts')

    # Admin
    status = models.CharField(max_length=30, choices=status_choices, default='active', verbose_name="Project status")

    description = models.TextField('Description', blank=True, null=True, help_text="Short description of the project.")

    misc_textareas = DictionaryField(blank=True, null=True)

    extra_info = DictionaryField(blank=True, null=True)

    def get_absolute_url(self):
        return reverse('ecosystems:project-detail', args=[str(self.id)])

    def __str__(self):
        return self.cedar_project_code + ": " + self.cedar_project_name

    class Meta:
        permissions = (
            ('view_ecosystemsproject', 'Can view ecosystems projects'),
        )

    # note: the object manager annotates the querysets with "cedar_project_code_q" field
    # that makes the field filterable/sortable etc.
    objects = EcosystemsProjectObjectManager()

    @property
    def cedar_project_code(self):
        prefix = self.get_project_code_prefix()
        return "{}{}".format(prefix, self.id)

    @classmethod
    def get_project_code_prefix(cls):
        '''
        This will create a harvest code prefix if the prefix is still only a string coming from the settings library.
        :return:
        '''
        prefix_setting = GeneralSetting.objects.get('ecosystems_project_code_prefix')

        # If the prefix is still a lame old string, make it a Harvest Code Prefix object
        # I need it for the DBViews builder.
        if isinstance(prefix_setting, str):
            hcp, created = HarvestCodePrefix.objects.get_or_create(
                prefix=prefix_setting,
                content_type=ContentType.objects.get_for_model(EcosystemsProject))
            GeneralSetting.objects.set('ecosystems_project_code_prefix', hcp, 'reference')
            return prefix_setting
        elif isinstance(prefix_setting, HarvestCodePrefix):
            return prefix_setting.prefix
        return None

    @classmethod
    def get_default_serializer_class(cls):
        '''
        Gets the default serializer class for this model.
        :return:
        '''
        # Put the import here, was getting circular import errors if not.
        import ecosystems.serializers
        return ecosystems.serializers.EcosystemsProjectSerializer

    def get_asset_class(self):
        '''
        Gets the default asset class for this model, instantiate with req'd variables and return.
        This should probably be switched to classmethod
        :return: instantiated asset class - NOT saved.
        '''

        return EcosystemsProjectAsset(
            project=self
        )


class EcosystemsAsset(assets.models.SecureAsset):
    @property
    def storage_string(self):
        return "ecosystems_assets"

    objects = InheritanceManager()

    @property
    def source_url(self):
        '''
        Return a link to the page in the UI for this asset (project details, interview
        details, session details, etc.
        :return:
        '''
        child = self.get_child_model()
        if child is not None:
            return child.source_url
        else:
            return reverse('ecosystems:secureasset-dashboard')

    @property
    def source_string(self):
        child = self.get_child_model()
        if child is not None:
            return child.source_string
        else:
            return 'Ecosystems ' + GeneralSetting.objects.get('assets__default_asset_source_string')

    def get_child_model(self):
        '''
        Assumes that an eco asset is inherited by
        one type of child model only:
        :return:
        '''
        try:
            return self.ecosystemsprojectasset
        except EcosystemsProjectAsset.DoesNotExist as e:
            pass
        return None

    def get_absolute_url(self):
        """
        Checks if there is a child asset type (eco project) and returns that url
        if possible, otherwise returns url to a generic dev't asset.
        :return:
        """
        child = self.get_child_model()
        if child:
            return child.get_absolute_url()
        else:
            return reverse('ecosystems:secureasset-detail', args=[self.id])

    class Meta:
        verbose_name = "Ecosystems File"


class EcosystemsProjectAsset(EcosystemsAsset):
    project = models.ForeignKey(EcosystemsProject)

    @property
    def storage_string(self):
        parent_storage = super(EcosystemsProjectAsset, self).storage_string
        this_storage = asset_helpers.generate_project_asset_storage_string(self.project)
        return '/'.join([parent_storage, this_storage])

    @property
    def source_url(self):
        return reverse("ecosystems:project-detail", args=[self.project.id])

    @property
    def source_string(self):
        return str(self.project)

    def get_absolute_url(self):
        return reverse('ecosystems:project-secureasset-detail', args=[self.project.id, self.id])

    class Meta:
        verbose_name = "Ecosystems Project File"


class EcosystemsGISLayer(GISLayerMaster):
    """
    This layer can be one of two important types: Misc or Not Misc.
    Not Misc means the "project" foreign key is not null and points to a EcosystemsProject.
    Absolute url, edit url, delete url, string name, etc. all change depending on whether
        it's a Misc Layer or not.
    """
    # layer_type_value = 'Ecosystems'
    project = models.ForeignKey('EcosystemsProject', blank=True, null=True)

    def get_absolute_url(self):
        if not self.is_misc():
            return reverse('ecosystems:project-detail', kwargs={'pk': self.project.pk})
        else:
            return reverse('ecosystems:gislayer-detail', kwargs={'pk': self.pk})

    def get_edit_url(self):
        if not self.is_misc():
            return reverse('ecosystems:project-location-edit', kwargs={'project_pk': self.project.pk, 'pk': self.pk})
        else:
            return reverse('ecosystems:gislayer-update', kwargs={'pk': self.pk})

    def get_delete_url(self):
        if not self.is_misc():
            return reverse('ecosystems:project-location-delete', kwargs={'project_pk': self.project.pk, 'pk': self.pk})
        else:
            return reverse('ecosystems:gislayer-delete', kwargs={'pk': self.pk})

    @classmethod
    def suggest_layer_name(cls, ecosystems_project):
        # Loop the counter until we have a gis layer name that is unique for this project:
        layer_count = EcosystemsGISLayer.objects.filter(project=ecosystems_project).count()
        while True:
            name = ecosystems_project.cedar_project_code + ' Layer ' + str(layer_count + 1)

            # Check name doesn't conflict, stop if it doesn't:
            if EcosystemsGISLayer.objects.filter(name=name, project=ecosystems_project).count() == 0:
                break
            else:
                layer_count += 1

        return name

    @property
    def layer_type_value(self):
        if self.is_misc():
            return 'Ecosystems Misc.'
        else:
            return 'Ecosystems'

    def is_misc(self):
        """
        Determines if this layer is a Misc or not.
        :return:
        """
        if self.project:
            return False
        else:
            return True

    def __str__(self):
        if self.is_misc():
            return "(ECO-M) {}".format(self.name)
        else:
            return "(ECO-{}) {}".format(self.project.id, self.name)


class FilingCode(MPTTModel):
    code = models.CharField(max_length=200, unique=True)
    label = models.CharField(max_length=200, unique=True)
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', db_index=True)

    def __str__(self):
        return self.label

    class MPTTMeta:
        order_insertion_by = ['code']


class ProjectTag(models.Model):
    tag = models.CharField("Tag text", max_length=30, blank=False, null=False)

    def __str__(self):
        return self.tag


class AlternateSpeciesName(models.Model):
    """ I know this is kind of sily, but with alternate names showing up more than once
    I'd prefer there was a common ancestor in case any changes need made, even if only to max_length.
    """
    name = models.CharField(max_length=200)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class PlantTag(TagBase):
    """
    Add extra fields here if needed
    """
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Plant"
        verbose_name_plural = "Plants"

    def get_absolute_url(self):
        from django.core.urlresolvers import reverse_lazy
        return reverse_lazy('ecosystems:planttag-detail', args=[self.id])


class PlantTaggedItem(GenericTaggedItemBase):
    tag = models.ForeignKey(PlantTag, related_name="%(app_label)s_%(class)s_items")


class CommonPlantName(AlternateSpeciesName):
    plant = models.ForeignKey('PlantTag', related_name='common_names')


class IndigenousPlantName(AlternateSpeciesName):
    plant = models.ForeignKey('PlantTag', related_name='indigenous_names')


class AnimalTag(TagBase):
    """
    Add extra fields here if needed
    """
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Animal"
        verbose_name_plural = "Animals"

    def get_absolute_url(self):
        from django.core.urlresolvers import reverse_lazy
        return reverse_lazy('ecosystems:animaltag-detail', args=[self.id])


class AnimalTaggedItem(GenericTaggedItemBase):
    tag = models.ForeignKey(AnimalTag, related_name="%(app_label)s_%(class)s_items")


class CommonAnimalName(AlternateSpeciesName):
    animal = models.ForeignKey('AnimalTag', related_name='common_names')


class IndigenousAnimalName(AlternateSpeciesName):
    animal = models.ForeignKey('AnimalTag', related_name='indigenous_names')
