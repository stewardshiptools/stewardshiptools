from django.core.urlresolvers import reverse
from django.contrib.gis.db import models
from django.db.models import Q, F, Value, CharField
from django.db.models.functions import Concat
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericRelation
from django_hstore.hstore import DictionaryField, HStoreGeoManager, HStoreManager
from model_utils.managers import InheritanceManager
from mptt.models import MPTTModel, TreeForeignKey
from taggit.managers import TaggableManager
import psycopg2

from django.db import connection

from crm.models import Person, Organization
from assets.models import SecureAsset
from assets import asset_helpers
from geoinfo.models import GISLayerMaster
from communication.models import HarvestCodePrefix, CommunicationRelation
from cedar_settings.models import GeneralSetting
from actions.models import ActionMaster
from tags.models import TaggedItem

from threadedcomments.models import ThreadedComment


# ------------------------------------
# Managers
# ------------------------------------
class DevelompentProjectObjectManager(HStoreManager):
    def get_queryset(self):
        '''
        Override get_queryset to annotate objects with the cedar_project_code_q field
        :return:
        '''
        qs = super(DevelompentProjectObjectManager, self).get_queryset()

        default_prefix_instance = DevelopmentProject.get_project_code_prefix()

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


# ------------------------------------
# Models
# ------------------------------------
class FileNo(models.Model):
    org_type_choices = (
        ('government', 'Government'),
        ('proponent', 'Proponent'),
        ('other', 'Other'),
    )

    project = models.ForeignKey('DevelopmentProject')
    file_number = models.CharField(max_length=200, blank=False, null=False)
    org_type = models.CharField(max_length=30, choices=org_type_choices)
    organization = models.ForeignKey(Organization, blank=True, null=True)

    def __str__(self):
        # looks really bad in the react list.
        # return "{} {}".format(self.organization, self.file_number)
        return self.file_number


class FilingCode(MPTTModel):
    code = models.CharField(max_length=200, unique=True)
    label = models.CharField(max_length=200, unique=True)
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', db_index=True)

    def __str__(self):
        return self.label

    class MPTTMeta:
        order_insertion_by = ['code']


class DevelopmentProject(models.Model):
    status_choices = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    )

    decision_choices = [
        ('pending', 'Pending'),
        ('approved', 'Recommended'),
        ('rejected', 'Not Recommended'),
    ]

    cedar_project_name = models.CharField(max_length=250, blank=False, null=False)

    # Codes
    # cedar_project_number = models.IntegerField('Cedar project number', blank=False, null=False)
    # cedar_project_code example = CEDAR-GN-23, where 23 is the cedar_project_number
    highlight = models.BooleanField(default=False)
    filing_code = TreeForeignKey('FilingCode', blank=True, null=True)

    # Dates
    initial_date = models.DateField('Initial Contact Date', blank=True, null=True,
                                    help_text='Date on which first contact was made.')
    due_date = models.DateField('Due Date', blank=True, null=True,
                                    help_text='Whichever due date is of concern.')

    # CRM / Persons
    cedar_assessor = models.ManyToManyField(Person, related_name='cedar_assessor', blank=True, verbose_name='Nation assessor')
    government_contact = models.ManyToManyField(Person, blank=True, related_name='government_contact')
    company_contact = models.ManyToManyField(Person, blank=True, related_name='company_contact')
    company = models.ForeignKey(Organization, blank=True, null=True)

    # Admin
    consultation_stage = models.ForeignKey('ConsultationStage', blank=True, null=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=30, choices=status_choices, default='active', verbose_name="Project status")
    final_decision = models.CharField(max_length=100, choices=decision_choices, default='pending', verbose_name="FN Final Decision")

    # Information Package
    primary_authorization = models.CharField(max_length=200, blank=True, null=True)  # Choicefield, see forms.py
    area = models.CharField(max_length=200, blank=True, null=True)
    description = models.TextField('Description', blank=True, null=True, help_text="Short description of project/permit.")
    rationale = models.TextField('Rationale', blank=True, null=True)
    location_description = models.TextField('Location Description', blank=True, null=True, help_text="Short description of the project's location.")

    misc_textareas = DictionaryField(blank=True, null=True)

    extra_info = DictionaryField(blank=True, null=True)

    comm_relationships = GenericRelation(CommunicationRelation, related_query_name='developmentprojects', object_id_field='related_object_oid', content_type_field='related_object_ct')
    comments = GenericRelation(ThreadedComment, related_query_name='developmentprojects', object_id_field='object_pk')

    def get_absolute_url(self):
        return reverse('development:project-detail', args=[str(self.id)])

    def __str__(self):
        return self.cedar_project_code + ": " + self.cedar_project_name

    class Meta:
        permissions = (
            ('view_developmentproject', 'Can view development projects'),
        )

    # note: the object manager annotates the querysets with "cedar_project_code_q" field
    # that makes the field filterable/sortable etc.
    objects = DevelompentProjectObjectManager()
    tags = TaggableManager(through=TaggedItem, blank=True)

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
        prefix_setting = GeneralSetting.objects.get('development_project_code_prefix')

        # If the prefix is still a lame old string, make it a Harvest Code Prefix object
        # I need it for the DBViews builder.
        if isinstance(prefix_setting, str):
            hcp, created = HarvestCodePrefix.objects.get_or_create(
                prefix=prefix_setting,
                content_type=ContentType.objects.get_for_model(DevelopmentProject))
            GeneralSetting.objects.set('development_project_code_prefix', hcp, 'reference')
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
        import development.serializers
        return development.serializers.DevelopmentProjectSerializer

    def get_asset_class(self):
        '''
        Gets the default asset class for this model, instantiate with req'd variables and return.
        This should probably be switched to classmethod
        :return: instantiated asset class - NOT saved.
        '''

        return DevelopmentProjectAsset(
            project=self
        )


class ConsultationStage(models.Model):
    stage_name = models.CharField('Consultation stage name', max_length=150, blank=False, null=False)
    stage_weight = models.IntegerField('Stage weighting', default=0)

    def __str__(self):
        return self.stage_name

    class Meta:
        ordering = ['stage_weight', ]


class DevelopmentGISLayer(GISLayerMaster):
    """
    This layer can be one of two important types: Misc or Not Misc.
    Not Misc means the "project" foreign key is not null and points to a DevelopmentProject.
    Absolute url, edit url, delete url, string name, etc. all change depending on whether
        it's a Misc Layer or not.
    """
    # layer_type_value = 'Development'
    project = models.ForeignKey('DevelopmentProject', blank=True, null=True)

    def get_absolute_url(self):
        if not self.is_misc():
            return reverse('development:project-detail', kwargs={'pk': self.project.pk})
        else:
            return reverse('development:gislayer-detail', kwargs={'pk': self.pk})

    def get_edit_url(self):
        if not self.is_misc():
            return reverse('development:project-location-edit', kwargs={'project_pk': self.project.pk, 'pk': self.pk})
        else:
            return reverse('development:gislayer-update', kwargs={'pk': self.pk})

    def get_delete_url(self):
        if not self.is_misc():
            return reverse('development:project-location-delete', kwargs={'project_pk': self.project.pk, 'pk': self.pk})
        else:
            return reverse('development:gislayer-delete', kwargs={'pk': self.pk})

    @classmethod
    def suggest_layer_name(cls, development_project):
        # Loop the counter until we have a gis layer name that is unique for this project:
        layer_count = DevelopmentGISLayer.objects.filter(project=development_project).count()
        while True:
            name = development_project.cedar_project_code + ' Layer ' + str(layer_count + 1)

            # Check name doesn't conflict, stop if it doesn't:
            if DevelopmentGISLayer.objects.filter(name=name, project=development_project).count() == 0:
                break
            else:
                layer_count += 1

        return name

    @property
    def layer_type_value(self):
        if self.is_misc():
            return 'Development Misc.'
        else:
            return 'Development'

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
            return "(DEV-M) {}".format(self.name)
        else:
            return "(DEV-{}) {}".format(self.project.id, self.name)


class DevelopmentAction(ActionMaster):
    pass


class DevelopmentProjectAction(DevelopmentAction):
    project = models.ForeignKey("DevelopmentProject")

######################################################
# Assets:
######################################################


class DevelopmentAsset(SecureAsset):
    @property
    def storage_string(self):
        return "development_assets"

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
            return reverse('development:secureasset-dashboard')

    @property
    def source_string(self):
        child = self.get_child_model()
        if child is not None:
            return child.source_string
        else:
            return 'Development ' + GeneralSetting.objects.get('assets__default_asset_source_string')

    def get_child_model(self):
        '''
        Assumes that a dev asset is inherited by
        one type of child model only:
        :return:
        '''
        try:
            return self.developmentprojectasset
        except DevelopmentProjectAsset.DoesNotExist as e:
            pass
        return None

    def get_absolute_url(self):
        """
        Checks if there is a child asset type (dev't project) and returns that url
        if possible, otherwise returns url to a generic dev't asset.
        :return:
        """
        child = self.get_child_model()
        if child:
            return child.get_absolute_url()
        else:
            return reverse('development:secureasset-detail', args=[self.id])

    class Meta:
        verbose_name = "Develoment File"


class DevelopmentProjectAsset(DevelopmentAsset):
    project = models.ForeignKey(DevelopmentProject)

    @property
    def storage_string(self):
        parent_storage = super(DevelopmentProjectAsset, self).storage_string
        this_storage = asset_helpers.generate_project_asset_storage_string(self.project)
        return '/'.join([parent_storage, this_storage])

    @property
    def source_url(self):
        return reverse("development:project-detail", args=[self.project.id])

    @property
    def source_string(self):
        return str(self.project)

    def get_absolute_url(self):
        return reverse('development:project-secureasset-detail', args=[self.project.id, self.id])

    class Meta:
        verbose_name = "Development Project File"
