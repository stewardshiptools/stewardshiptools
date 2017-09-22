import uuid
import logging
from django.contrib.gis.db import models
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.conf import settings
from filer.fields.image import FilerImageField
from crm.models import Person
from assets.models import SecureAsset
from assets import asset_helpers
from model_utils.managers import InheritanceManager
from django_hstore import hstore

from cedar.models import PrefixedIDModelAbstract

from taggit.managers import TaggableManager
from taggit.models import TagBase, TaggedItemBase, ItemBase

from geoinfo.models import GISLayerMaster, GISFeature

from cedar_settings.models import GeneralSetting

from communication.models import HarvestCodePrefix

from maps.models import CompositeStyle

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class Interview(models.Model):
    type_choices = (('video', 'Video'), ('audio', 'Audio'))

    # 'participant' - This is handled in the crm.Person model as a foreign key to Interview.
    # todo Check that phase is synonymous with project.
    phase = models.ForeignKey('Project')  # This should be renamed to project
    date = models.DateTimeField('DateTime', blank=True, null=True, help_text='Date & time of the interview')
    primary_interviewer = models.ForeignKey(Person, related_name='interviews_conducted', blank=True, null=True)
    other_interviewers = models.ManyToManyField(Person, blank=True, related_name='interviews_assisted')
    participant_number = models.IntegerField('Participant number', blank=False)
    # todo Should community be a link to a "place"? Are we going to have a gazetted Place model at some point?
    community = models.CharField('Community', max_length=300)
    type = models.CharField(choices=type_choices, blank=False, max_length=5)
    participants = models.ManyToManyField(Person, blank=True)
    attendees = models.ManyToManyField(Person, blank=True, related_name="interviews_attended")

    related_items = models.ManyToManyField('library.Item', blank=True, related_name='related_heritage_interviews')

    class Meta:
        unique_together = ('phase', 'primary_interviewer', 'type', 'participant_number')
        permissions = (
            ("view_interview", "Can view interview"),
            ('view_sensitive_interview_data', 'Can view sensitive interview data')
        )

    def get_absolute_url(self):
        return reverse('heritage:interview-detail', kwargs={'pk': self.pk})

    @property
    def interviewer_initials(self):
        # return InterviewerId.objects.get(interviewer_id=self.interviewer_id).interviewer_id
        return self.primary_interviewer.initials

    @property
    def interview_number_string(self):
        return str(self.participant_number).zfill(3)

    def __str__(self):
        if settings.IS_HAIDA:
            return '{} {} {} {}'.format(
                self.phase, self.primary_interviewer.initials, self.type, self.interview_number_string)
        else:
            return '{} {}'.format(
                self.phase, self.interview_number_string)


class Session(models.Model):
    """
    A single interview will typically have been broken up into multiple sessions.
    """
    # todo Extend this with the contents of the Missing worksheet.

    transcript_file_choices = (('trans1', 'trans1'), ('trans2', 'trans2'), ('trans3', 'trans3'), ('trans4', 'trans4'),
                               ('trans5', 'trans5'), ('trans6', 'trans6'), ('trans7', 'trans7'), ('trans8', 'trans8'),
                               ('trans5', 'trans5'), ('trans6', 'trans6'), ('trans7', 'trans7'), ('trans8', 'trans8'),
                               ('trans9', 'trans9'), ('trans10', 'trans10'), ('trans11', 'trans11'))

    interview = models.ForeignKey(Interview)
    number = models.CharField('Session number', blank=False, max_length=3)
    date = models.DateField('Date', blank=True, null=True, help_text='Date on which the interview session occurred.')
    # todo Is this an asset? A separate type of asset? Just a text field with choices?
    transcript_file = models.CharField('Transcript file', blank=True, max_length=15, choices=transcript_file_choices)
    # Alternatively duration could be stored as a number of seconds, or TimeField, or... ?
    duration = models.CharField('Duration', blank=True, max_length=7)
    # Could optionally be an asset FK to the actual file, but we're not actually planning to do anything with the audio.
    audio_file_code = models.CharField('Audio file code', blank=True, max_length=40)
    audio_files = models.CharField('Audio files', blank=True, max_length=200)
    video_files = models.CharField('Video files', blank=True, max_length=200)
    # Similarly Transcript file code could be an asset link or just the text code.
    transcription_file_code = models.CharField('Audio file code', blank=True, max_length=24)
    checked_by_interviewer = models.CharField('Checked by interviewer', blank=True, max_length=15)
    corrected_by_jw = models.NullBooleanField('Corrected by JW', blank=True, max_length=3)
    # This does seem to vary among sessions in a few cases.
    sent_for_archiving = models.DateField('Sent for archiving', blank=True, null=True)
    copy_given_to_participant = models.DateField('Copy given to participant', blank=True, null=True)
    janet_notes = models.TextField('Janet notes', blank=True)
    notes_on_files = models.TextField('Notes on files', blank=True)
    other_media = models.TextField('Other media', blank=True)
    missing = models.TextField('Missing', blank=True)
    final_transcript_from_janet = models.NullBooleanField('Final transcript from Janet?')
    notes = models.TextField(blank=True, null=True, verbose_name="General notes on session record.")

    class Meta:
        unique_together = ('interview', 'number')
        permissions = (
            ("view_session", "Can view session"),
        )

    def __str__(self):
        return '{} {}'.format(self.interview, str(self.number).zfill(2))


class Project(models.Model):
    name = models.CharField('Name', blank=False, max_length=100)

    picture = models.ImageField(blank=True, null=True, upload_to='heritage')

    phase_code = models.CharField('Phase code', blank=True, null=True, max_length=8,
                                  help_text='Project phase code.')

    # We want to delete this later if possible, try to avoid using it.  It's also kind of useless...
    year_string = models.CharField('Year', blank=True, null=True, max_length=8,
                                   help_text='The year this project took place.', )
    start_date = models.DateField('Start date', blank=True, null=True)
    end_date = models.DateField('End date', blank=True, null=True)
    location = models.CharField('Location', max_length=300, blank=True)
    background = models.TextField('Background', blank=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('heritage:project-detail', args=[str(self.id)])

    @property
    def participant_count(self):
        unique_set = Person.objects.none()

        for i in self.interview_set.all():
            unique_set = unique_set | i.participants.filter()

        return unique_set.count()

    @property
    def document_count(self):
        return ProjectAsset.objects.filter(project=self).count() \
               + InterviewAsset.objects.filter(interview__phase=self).count() \
               + SessionAsset.objects.filter(session__interview__phase=self).count()

    class Meta:
        permissions = (
            ("view_project", "Can view project"),
        )
        ordering = ('start_date', 'end_date', 'name')

    @classmethod
    def get_default_serializer_class(cls):
        '''
        Gets the default serializer class for this model.
        :return:
        '''
        # Put the import here, was getting circular import errors if not.
        import heritage.serializers
        return heritage.serializers.ProjectSerializer

    def get_asset_class(self):
        '''
        Gets the default asset class for this model, instantiate with req'd variables and return.
        This should probably be switched to classmethod
        :return: instantiated asset class - NOT saved.
        '''

        return ProjectAsset(
            project=self
        )

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
        prefix_setting = GeneralSetting.objects.get('heritage_project_code_prefix')

        # If the prefix is still a lame old string, make it a Harvest Code Prefix object
        # I need it for the DBViews builder.
        if isinstance(prefix_setting, str):
            hcp, created = HarvestCodePrefix.objects.get_or_create(
                prefix=prefix_setting,
                content_type=ContentType.objects.get_for_model(Project))
            GeneralSetting.objects.set('heritage_project_code_prefix', hcp, 'reference')
            return prefix_setting
        elif isinstance(prefix_setting, HarvestCodePrefix):
            return prefix_setting.prefix
        return None


class Record(models.Model):
    name = models.CharField(max_length=200)
    session = models.ForeignKey('Session', blank=True, null=True)
    published = models.BooleanField(default=True)

    objects = InheritanceManager()

    class Meta:
        permissions = [
            ("view_record_meta", "Can view meta data in records.")
        ]


class MTKRecord(Record):
    """
    This parent data model consolidates and enforces consistency for the many fields that are common between the
    species and feature/place data types of the HMTK project.
    """
    objects = InheritanceManager()

    map_feature = models.CharField('Map feature', blank=True, max_length=10)
    # "link code" is just a composite of project + interview id + participant id + interview #  + map feature.
    # Better to ignore it and query against those others. Keeping it for now just in case.
    link_code = models.CharField('Link code', blank=True, max_length=25)
    verification_required = models.BooleanField('Verification required?', blank=False, default=False)
    # todo Link MTK to an actual interview (session?)
    interview_number = models.IntegerField('Interview number', blank=True, null=True)
    interview = models.ForeignKey('Interview', blank=True, null=True)
    comments = models.TextField('Comments', blank=True)
    project = models.ForeignKey('Project', default=1)
    interviewer = models.ForeignKey(Person, null=True, blank=True)
    participant_id = models.IntegerField('Participant ID', null=True, blank=True)
    participant_secondary_id = models.CharField('Secondary Participant ID', max_length=10, null=True, blank=True)
    data_entry_id = models.ForeignKey('DataEntryId', default=1)
    shape_type = models.ForeignKey('ShapeType', blank=True, null=True)
    shape_type_inferred = models.BooleanField('Shape type inferred?', default=False)
    base_map = models.CharField('Base map', max_length=30, blank=True, null=True)
    scan = models.IntegerField('Scan', default=0)
    data_source = models.ForeignKey('DataSource', blank=True, null=True)
    data_source_inferred = models.BooleanField(default=False)
    info_type = models.ForeignKey('InfoType', default=1)
    accuracy = models.ForeignKey('Accuracy', blank=True, null=True)
    gazetted_place_name = models.CharField('Gazetted place name', max_length=200, blank=True)
    local_place_name = models.CharField('Local place name', max_length=200, blank=True)
    first_nations_place_name = models.CharField('First Nations place name', max_length=200, blank=True)
    linguistic_group = models.ForeignKey('LinguisticGroup', blank=True, null=True)
    linguistic_group_inferred = models.BooleanField('Linguistic group inferred?', default=False)
    seasons = models.ManyToManyField('Season', blank=True)
    season_inferred = models.BooleanField(default=False)
    use = models.ForeignKey('Use', blank=True, null=True)
    use_other_detail = models.CharField('Use other detail', blank=True, max_length=30,
                                        help_text='If use coded as "other", what was written in?')
    use_inferred = models.BooleanField('Use inferred?', default=False)
    time_frame_start = models.ForeignKey('TimeFrame', blank=True, null=True, related_name='starts')
    time_frame_start_inferred = models.BooleanField('Time frame inferred?', default=False)
    time_frame_end = models.ForeignKey('TimeFrame', blank=True, null=True, related_name='ends')
    time_frame_end_inferred = models.BooleanField('Time frame inferred?', default=False)
    time_frame_comments = models.TextField('Time frame comments', blank=True)
    quotes = models.TextField('Quotes', blank=True)
    comments_2 = models.TextField('Comments', blank=True)  # Yes there are 2 comments fields.
    related_documents = models.CharField('Related documents', blank=True, max_length=200)
    notes_for_map = models.CharField('Notes for map', blank=True, max_length=200)
    checked_by_kb = models.CharField('Checked by KB', blank=True, max_length=300)
    participant_community = models.CharField('Participant community', blank=True, null=True, default='pending',
                                             max_length=100)
    harvest_method = models.ForeignKey('HarvestMethod', blank=True, null=True,
                                       help_text='Harvest method/observation type')
    in_gdb = models.BooleanField(default=True)
    in_transcripts = models.BooleanField(default=True)

    def __str__(self):
        return self.link_code


class MTKCulturalRecord(MTKRecord):
    """
    This model holds information that is specific to place/feature-based MTK spatial data.
    It can be further sub-classed to implement specific geographic types (point, line, polygon, multipolygon).
    """
    group = models.ForeignKey('Group', default=1)
    # A given record may be assigned more than one feature type, e.g. cultural = 'visi', management = 'inre'.
    ecological_feature = models.ForeignKey('Feature', blank=True, null=True, related_name='ecological')
    ecological_feature_other_detail = models.CharField('Ecological feature other detail', blank=True, max_length=30,
                                                       help_text='If ecological feature coded as "other", what was written in?')
    ecological_feature_inferred = models.BooleanField(default=False)
    cultural_feature = models.ForeignKey('Feature', blank=True, null=True, related_name='cultural')
    cultural_feature_other_detail = models.CharField('Cultural feature other detail', blank=True, max_length=30,
                                                     help_text='If cultural feature coded as "other", what was written in?')
    cultural_feature_inferred = models.BooleanField(default=False)
    industrial_feature = models.ForeignKey('Feature', blank=True, null=True, related_name='industrial')
    industrial_feature_other_detail = models.CharField('Industrial feature other detail', blank=True, max_length=30,
                                                       help_text='If cultural feature coded as "other", what was written in?')
    industrial_feature_inferred = models.BooleanField(default=False)
    management_feature = models.ForeignKey('Feature', blank=True, null=True, related_name='management')
    management_feature_other_detail = models.CharField('Management feature other detail', blank=True, max_length=30,
                                                       help_text='If management feature coded as "other", what was written in?')
    management_feature_inferred = models.BooleanField(default=False)
    value_feature = models.ForeignKey('Feature', blank=True, null=True, related_name='value')
    value_feature_other_detail = models.CharField('Value feature other detail', blank=True, max_length=30,
                                                  help_text='If value feature coded as "other", what was written in?')
    value_feature_inferred = models.BooleanField(default=False)
    travel_mode = models.ForeignKey('TravelMode', blank=True, null=True)
    travel_mode_inferred = models.BooleanField('Travel Mode inferred?', default=False)
    target_species = models.ForeignKey('Species', blank=True, null=True, related_name='target')
    target_species_inferred = models.BooleanField('Target species inferred?', default=False)
    target_species_other_detail = models.CharField('Target species other detail', blank=True, max_length=30,
                                                   help_text='If target species coded as "other", what was written in?')
    secondary_species = models.ForeignKey('Species', blank=True, null=True, related_name='secondary')
    secondary_species_inferred = models.BooleanField('Secondary species inferred?', default=False)
    secondary_species_other_detail = models.CharField('Secondary species other detail', blank=True, max_length=30,
                                                      help_text='If secondary species coded as "other", what was written in?')

    objects = InheritanceManager()


class MTKCulturalRecordPoint(MTKCulturalRecord):
    geometry = models.PointField()
    objects = models.GeoManager()


class MTKCulturalRecordLine(MTKCulturalRecord):
    geometry = models.MultiLineStringField()
    objects = models.GeoManager()


class MTKCulturalRecordPolygon(MTKCulturalRecord):
    geometry = models.MultiPolygonField()
    objects = models.GeoManager()


class MTKSpeciesRecord(MTKRecord):
    """
    This model holds information that is specific to species-based MTK spatial data.
    It can be further sub-classed to implement specific geographic types (point, line, polygon, multipolygon).
    """
    species = models.ForeignKey('Species', default=1, blank=True, null=True)
    species_inferred = models.BooleanField(default=False)
    species_other_detail = models.CharField('Species other detail', blank=True, max_length=30,
                                                     help_text='If value feature coded as "other", what was written in?')
    fishing_method = models.ForeignKey('FishingMethod', blank=True, null=True)
    fishing_method_inferred = models.BooleanField('Fishing method inferred?', default=False)
    fishing_method_other_detail = models.CharField('Fishing method other detail', blank=True, max_length=30,
                                                   help_text='If value feature coded as "other", what was written in?')
    ecological_value = models.ForeignKey('EcologicalValue', blank=True, null=True)
    ecological_value_inferred = models.BooleanField('Ecological value inferred?', default=False)
    temporal_trend = models.ForeignKey('TemporalTrend', blank=True, null=True)
    temporal_trend_inferred = models.BooleanField('Temporal trend inferred?', default=False)
    temporal_trend_comment = models.TextField('Temporal trend comment', blank=True)
    f34 = models.CharField('F34', blank=True, null=True, max_length=200)  # This seems to be 'notes for map 2'?
    species_theme = models.ForeignKey('SpeciesTheme', blank=True, null=True)
    # "It was a field created to identify all species records which were ecological observations only
    # and not related to harvest or other use." -- Chris. Needed? Infer-able from the other data?
    ecological_observation_only = models.NullBooleanField('Ecological observation only?', default=False)

    objects = InheritanceManager()


class MTKSpeciesRecordPoint(MTKSpeciesRecord):
    geometry = models.PointField()
    objects = models.GeoManager()


class MTKSpeciesRecordLine(MTKSpeciesRecord):
    geometry = models.MultiLineStringField()
    objects = models.GeoManager()


class MTKSpeciesRecordPolygon(MTKSpeciesRecord):
    geometry = models.MultiPolygonField()
    objects = models.GeoManager()


class RecordSessionLink(models.Model):
    record = models.ForeignKey('Record')
    session = models.ForeignKey('Session')
    comment_number = models.PositiveSmallIntegerField(blank=True, null=True)
    page_number = models.PositiveSmallIntegerField(blank=True, null=True)
    line_number = models.PositiveSmallIntegerField(blank=True, null=True)
    spatial_code = models.CharField(max_length=200, blank=True, null=True)

    # In the case of HMTK this is usually some representation of one or multiple spatial codes.
    original_comment_on_map = models.CharField(max_length=200, blank=True, null=True)

    transcript_excerpt = models.TextField(blank=True, null=True, help_text="This is the transcript text that the record"
                                                                           "was created for.")
    transcript_excerpt_full = models.TextField(blank=True, null=True, help_text="This is the transcript text used"
                                                                                "above,with surrounding lines for"
                                                                                "context.")

    class Meta:
        ordering = ['session__date', 'record__name']

    def __str__(self):
        return "%s <- %s" % (self.session, self.record.name)


class ParticipantId(models.Model):
    """
    This provides a way to identify multiple MTK data that were provided by the same interviewee,
    without exposing the name of the interviewee to users without sufficient permissions.
    Note that in the cases where there were multiple interviewees for a single interview, geo-data entries
    are assigned to either "a", "b", or both interviewees, i.e. 3a, 4ab, etc.
    """

    # 'c' is not listed in the data documentation but shows up at least once in the data.
    participant_secondary_id_choices = (('a', 'a'), ('b', 'b'), ('ab', 'ab'), ('c', 'c'))

    participant_id = models.IntegerField('Participant ID', blank=False, default=0)
    participant_secondary_id = models.CharField('Participant secondary ID', blank=True, max_length=2,
                                                choices=participant_secondary_id_choices)
    person = models.ForeignKey('crm.Person', blank=True, null=True)

    def __str__(self):
        if self.participant_id:
            return str(self.participant_id)
        else:
            return 'None'


class InterviewerId(models.Model):
    """
    This maps interviewer initials as stored in the MTK data with individuals in the CRM.
    This is lazy - I could have just written a mapping table into the import script
    and made Interviewer a direct FK link to CRM and obviated this table entirely.
    This way the interviewer initials have a place to be stashed pending that research.
    """
    interviewer_id = models.CharField('Interviewer ID', blank=False, max_length=10)
    person = models.ForeignKey('crm.Person', blank=True, null=True)

    def __str__(self):
        if self.interviewer_id:
            return self.interviewer_id
        else:
            return 'None'


class DataEntryId(models.Model):
    """
    This stores the data enter-er's initials, and once we've researched who they represent, can map to the CRM.
    """
    data_entry_id = models.CharField('Data entry ID', blank=True, null=True, max_length=10)
    person = models.ForeignKey('crm.Person', blank=True, null=True)

    def __str__(self):
        if self.data_entry_id:
            return self.data_entry_id
        else:
            return 'None'


class Species(models.Model):
    """
    This represents the Species Codes sheet in the TK_Tables_Codes_October_2009.xls.
    """

    species_group = models.ForeignKey('SpeciesGroup', default=1)
    description = models.CharField('Description', blank=False, max_length=100)
    # In theory each species group has it's own 'other' category. But there's no way to tell from the data
    # which species group to use, so we'll just have to put them all entries under a single "other".
    # An implication of that is that database_code can be unique.
    database_code = models.CharField('Database code', blank=False, max_length=5, unique=True)
    other_detail = models.CharField('Other detail', blank=True, max_length=30,
                                    help_text='If coded as "other", what was written in?')
    name_equivalents = models.CharField('Name equivalents', blank=True, max_length=100)
    photo = FilerImageField(blank=True, null=True, related_name='species_photo')

    def __str__(self):
        if self.description:
            return self.description
        elif self.database_code:
            return self.database_code
        else:
            return 'None'

    class Meta:
        ordering = ['description']
        verbose_name_plural = 'species'


class SpeciesGroup(models.Model):
    """
    The species code tables include a "group" field which categorizes species.
    This simple data model implements those groupings.
    """

    name = models.CharField('Name', blank=False, max_length=20)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Feature(models.Model):
    """
    This represents the Feature Codes sheet in the TK_Tables_Codes_October_2009.xls.
    This should *perhaps* be broken out into CulturalFeature, ManagementFeature, etc. models.
    """
    feature_group = models.ForeignKey('FeatureGroup', default=1)
    description = models.CharField('Description', blank=False, max_length=100)
    database_code = models.CharField('Database code', blank=False, max_length=5, unique=True)

    comments = models.CharField('Comments', blank=True, max_length=200)

    def __str__(self):
        if self.description:
            return self.description
        elif self.database_code:
            return self.database_code
        else:
            return 'None'


class FeatureGroup(models.Model):
    """
    The feature code tables include a "group" field which categorizes features.
    This simple data model implements those groupings.
    """

    name = models.CharField('Name', blank=False, max_length=20)


class ShapeType(models.Model):
    """
    This represents the Shape Type codes in the Other Codes sheet in the TK_Tables_Codes_October_2009.xls.
    I guess this data should be kept, so we don't lose the indication of which were inferred and which weren't.
    """
    description = models.CharField('Description', blank=False, max_length=30)
    database_code = models.CharField('Database code', blank=False, max_length=5, unique=True)

    def __str__(self):
        if self.description:
            return self.description
        elif self.database_code:
            return self.database_code
        else:
            return 'None'


class DataSource(models.Model):
    """
    This represents the Data Source codes in the Other Codes sheet in the TK_Tables_Codes_October_2009.xls.
    """
    description = models.CharField('Description', blank=False, max_length=30)
    database_code = models.CharField('Database code', blank=False, max_length=2, unique=True)
    comments = models.CharField('Comments', blank=True, max_length=200)

    def __str__(self):
        if self.description:
            return self.description
        elif self.database_code:
            return self.database_code
        else:
            return 'None'


class InfoType(models.Model):
    """
    This represents the Info Type codes in the Other Codes sheet in the TK_Tables_Codes_October_2009.xls.
    """
    description = models.CharField('Description', blank=False, max_length=50)
    # These are integers but using CharField to avoid casting issues from the source data.
    database_code = models.CharField('Database code', blank=False, max_length=1, unique=True)
    comments = models.CharField('Comments', blank=True, max_length=100)

    def __str__(self):
        if self.description:
            return self.description
        elif self.database_code:
            return self.database_code
        else:
            return 'None'


class Accuracy(models.Model):
    """
    This represents the Accuracy codes in the Other Codes sheet in the TK_Tables_Codes_October_2009.xls.
    """
    description = models.CharField('Description', blank=False, max_length=50)
    database_code = models.CharField('Database code', blank=False, max_length=1, unique=True)

    def __str__(self):
        if self.description:
            return self.description
        elif self.database_code:
            return self.database_code
        else:
            return 'None'


class LinguisticGroup(models.Model):
    """
    This represents the Linguistic Group codes in the Other Codes sheet in the TK_Tables_Codes_October_2009.xls.
    """
    description = models.CharField('Description', blank=False, max_length=100)
    database_code = models.CharField('Database code', blank=False, max_length=4, unique=True)
    comments = models.CharField('Comments', blank=True, max_length=100)

    def __str__(self):
        if self.description:
            return self.description
        elif self.database_code:
            return self.database_code
        else:
            return 'None'


class Use(models.Model):
    """
    This represents the Use codes in the Other Codes sheet in the TK_Tables_Codes_October_2009.xls.
    """
    description = models.CharField('Description', blank=False, max_length=100)
    database_code = models.CharField('Database code', blank=False, max_length=4, unique=True)
    comments = models.CharField('Comments', blank=True, max_length=100)
    inferred = models.BooleanField('Inferred?', blank=False, default=False)

    def __str__(self):
        if self.description:
            return self.description
        elif self.database_code:
            return self.database_code
        else:
            return 'None'

    class Meta:
        ordering = ['description']


class FishingMethod(models.Model):
    """
    This represents the Fishing Method codes in the Other Codes sheet in the TK_Tables_Codes_October_2009.xls.
    """
    description = models.CharField('Description', blank=False, max_length=100)
    database_code = models.CharField('Database code', blank=False, max_length=5, unique=True)
    comments = models.CharField('Comments', blank=True, max_length=100)
    inferred = models.BooleanField('Inferred?', blank=False, default=False)

    def __str__(self):
        if self.description:
            return self.description
        elif self.database_code:
            return self.database_code
        else:
            return 'None'

    class Meta:
        ordering = ['description']


class EcologicalValue(models.Model):
    """
    This represents the Fishing Method codes in the Other Codes sheet in the TK_Tables_Codes_October_2009.xls.
    """
    description = models.CharField('Description', blank=False, max_length=100)
    database_code = models.CharField('Database code', blank=False, max_length=5, unique=True)
    comments = models.CharField('Comments', blank=True, max_length=100)

    def __str__(self):
        if self.description:
            return self.description
        elif self.database_code:
            return self.database_code
        else:
            return 'None'

    class Meta:
        ordering = ['description']


class Season(models.Model):
    """
    This represents the Season codes in the Other Codes sheet in the TK_Tables_Codes_October_2009.xls.
    """
    description = models.CharField('Description', blank=False, max_length=100)
    database_code = models.CharField('Database code', blank=False, max_length=4, unique=True)

    def __str__(self):
        if self.description:
            return self.description
        elif self.database_code:
            return self.database_code
        else:
            return 'None'


class TimeFrame(models.Model):
    """
    This represents the Time Frame codes in the Other Codes sheet in the TK_Tables_Codes_October_2009.xls.
    """
    description = models.CharField('Description', blank=False, max_length=100)
    database_code = models.CharField('Database code', blank=False, max_length=4, unique=True)

    def __str__(self):
        if self.description:
            return self.description
        elif self.database_code:
            return self.database_code
        else:
            return 'None'

    class Meta:
        ordering = ['description']


class TemporalTrend(models.Model):
    """
    This represents the Time Frame codes in the Other Codes sheet in the TK_Tables_Codes_October_2009.xls.
    """
    description = models.CharField('Description', blank=False, max_length=100)
    database_code = models.CharField('Database code', blank=False, max_length=4, unique=True)

    def __str__(self):
        if self.description:
            return self.description
        elif self.database_code:
            return self.database_code
        else:
            return 'None'


class TravelMode(models.Model):
    """
    This represents the Time Frame codes in the Other Codes sheet in the TK_Tables_Codes_October_2009.xls.
    """
    description = models.CharField('Description', blank=False, max_length=100)
    database_code = models.CharField('Database code', blank=False, max_length=4, unique=True)
    inferred = models.BooleanField('Inferred?', blank=False, default=False)

    def __str__(self):
        if self.description:
            return self.description
        elif self.database_code:
            return self.database_code
        else:
            return 'None'


class HarvestMethod(models.Model):
    """
    This holds the "Groupings__" field in the feature and species geo data.
    "These were fields that were used at various times to create groupings for common theme maps which were generated.
    We could call them Map_themes_#." -- Chris
    """
    name = models.CharField('Name', blank=False, max_length=100)

    def __str__(self):
        if self.name:
            return self.name
        else:
            return 'None'

    class Meta:
        ordering = ['name']


class SpeciesTheme(models.Model):
    """
    This will hold the "Species__1" field in the species geo data.
    "Similar to the thematic groupings … used to create broader categories for thematic maps and reports" -- Chris
    I'm not sure what to call this, so I'm picking something arbitrarily
    I don't expect this will get used, but keeping it just in case.
    """
    name = models.CharField('Name', blank=True, null=True, max_length=100)

    def __str__(self):
        if self.name:
            return self.name
        else:
            return 'None'

    class Meta:
        ordering = ['name']


class Group(models.Model):
    """
    This holds the "S_Group" field in the feature geo data.
    This should probably have a better name.
    """
    name = models.CharField('Name', blank=True, null=True, max_length=100, default='pending')

    def __str__(self):
        if self.name:
            return self.name
        else:
            return 'None'


class LayerGroup(models.Model):
    name = models.CharField(max_length=200, blank=True, null=True)
    data = hstore.DictionaryField(blank=True, null=True, help_text='This field is optional.')
    interview = models.ForeignKey("Interview")

    def get_absolute_url(self):
        return reverse('heritage:interview-detail', kwargs={'pk': self.interview.pk})

    def __str__(self):
        return self.name or "Dataset #%d" % self.id

    def get_features_ajax_url(self):
        return "%s?group=%d" % (reverse('heritage:api:sites-list'), self.pk)

    def features(self):
        layers = self.heritagegislayer_set.all()
        return GISFeature.objects.filter(layer__in=layers)


class HeritageGISLayer(GISLayerMaster):
    group = models.ForeignKey("LayerGroup", blank=True, null=True)

    def get_absolute_url(self):
        if not self.is_misc():
            return reverse('heritage:interview-detail', kwargs={'pk': self.group.interview.pk})
        else:
            return reverse('heritage:gislayer-detail', kwargs={'pk': self.pk})

    def get_edit_url(self):
        if not self.is_misc():
            return reverse('heritage:gislayer-update', kwargs={
                'interview_pk': self.group.interview.pk,
                'layergroup_pk': self.group.pk,
                'pk': self.pk
            })
        else:
            return reverse('heritage:gislayer-update-generic', kwargs={
                'pk': self.pk
            })

    def get_delete_url(self):
        if not self.is_misc():
            return reverse('heritage:gislayer-delete', kwargs={
                'interview_pk': self.group.interview.pk,
                'layergroup_pk': self.group.pk,
                'pk': self.pk
            })
        else:
            return reverse('heritage:gislayer-delete-generic', kwargs={
                'pk': self.pk
            })

    @property
    def layer_type_value(self):
        if not self.group:
            return 'Heritage Misc.'
        else:
            return 'Heritage'

    def is_misc(self):
        """
        Determines if this layer is a Misc or not.
        :return:
        """
        if self.group:
            return False
        else:
            return True

    def __str__(self):
        if self.is_misc():
            return "(HER-M) {}".format(self.name)
        else:
            return "(HER-{}) {}".format(self.group.interview.phase.id, self.name)


##########################
# Named places           #
##########################
class Place(PrefixedIDModelAbstract, models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    notes = models.TextField(blank=True, null=True)

    # Should this place show up on the community map?
    add_to_community_map = models.BooleanField(default=False)

    # I chose a geometryfield because it seems unclear what kind of location data the clients
    # want to associate with a named place.
    geometry = models.GeometryField(srid=4326)

    gazetteer_names = TaggableManager(through='GazetteerNameTaggedPlace', blank=True)

    place_types = models.ManyToManyField("PlaceType", blank=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("heritage:place-detail", kwargs={'pk': self.pk})

    @classmethod
    def get_prefix(cls):
        return "P-"

    @property
    def search_template(self):
        '''
        :return: path to default search result template.
        '''
        return 'search/results/place_result.html'

    @property
    def map_style(self):
        if self.place_types.count():
            named_place_qs = self.place_types.filter(place_type__iexact='named place')
            if named_place_qs.count() > 0:
                style_instance = named_place_qs.first().map_style
            else:
                style_instance = self.place_types.first().map_style
            return style_instance
        else:
            return None


class PlaceName(models.Model):
    name = models.CharField(max_length=200)
    place = models.ForeignKey("Place")

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class AlternatePlaceName(PlaceName):
    pass


class CommonPlaceName(PlaceName):
    pass


class GazetteerNameTag(TagBase):
    """ A custom tag model to provide a description field to Collection Tags.
    """
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Gazetteer Name"
        verbose_name_plural = "Gazetteer Names"


class GazetteerNameTaggedPlace(ItemBase):
    """
    Acts as the through model from Item <-> CollectionTag relationship
    It inherits from ItemBase and creates its own version of taggit.TaggedItemBase
        - TaggedItemBase.tag was not permitting me to use a custom tag model (CollectionTag).
    """
    tag = models.ForeignKey(GazetteerNameTag, related_name="%(app_label)s_%(class)s_items", on_delete=models.CASCADE)
    content_object = models.ForeignKey('Place')

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


class PlaceType(models.Model):
    place_type = models.CharField(max_length=200)
    map_style = models.ForeignKey(CompositeStyle, blank=True, null=True)

    def __str__(self):
        return self.place_type


######################################################
# Assets:
######################################################


class HeritageAsset(SecureAsset):
    @property
    def storage_string(self):
        return "heritage_assets"

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
            return reverse('heritage:secureasset-dashboard')

    @property
    def source_string(self):
        child = self.get_child_model()
        if child is not None:
            return child.source_string
        else:
            return 'Heritage ' + GeneralSetting.objects.get('assets__default_asset_source_string')

    @property
    def search_template(self):
        '''
        :return: path to default search result template.
        '''
        return 'search/results/heritageasset_result.html'

    def get_child_model(self):
        '''
        Assumes that a heritage asset is inherited by
        one type of child model only:
        :return:
        '''
        try:
            return self.projectasset
        except ProjectAsset.DoesNotExist as e:
            pass
        try:
            return self.interviewasset
        except InterviewAsset.DoesNotExist as e:
            pass
        try:
            return self.sessionasset
        except SessionAsset.DoesNotExist as e:
            pass

        return None

    # def get_absolute_url(self):
    #     return reverse('heritage:secureasset-detail', args=[self.id])

    def get_absolute_url(self):
        """
        Checks if there is a child asset type and returns that url
        if possible, otherwise returns url to a generic dev't asset.
        BE carefule: If you don't define a .get_absolute_url() method
        on the children you will end up in an infinite loop. Yikes.
        :return:
        """
        child = self.get_child_model()
        if child:
            return child.get_absolute_url()
        else:
            return reverse('heritage:secureasset-detail', args=[self.id])

    @property
    def download_url(self):
        return reverse('heritage:secureasset-download', args=[self.id])

    @property
    def serve_url(self):
        return reverse('heritage:secureasset-serve', args=[self.id])

    class Meta:
        verbose_name = "Heritage File"


class ProjectAsset(HeritageAsset):
    project = models.ForeignKey(Project)

    @property
    def storage_string(self):
        parent_storage = super(ProjectAsset, self).storage_string
        this_storage = asset_helpers.generate_heritage_project_asset_storage_string(self.project)
        return '/'.join([parent_storage, this_storage])

        # objects = InheritanceManager()

    @property
    def source_url(self):
        return reverse("heritage:project-detail", args=[self.project.id])

    @property
    def source_string(self):
        return str(self.project)

    def get_absolute_url(self):
        return reverse('heritage:project-secureasset-detail', args=[self.project.id, self.id])

    class Meta:
        verbose_name = "Heritage Project File"


class InterviewAsset(HeritageAsset):
    interview = models.ForeignKey(Interview)

    def __str__(self):
        return " - ".join([self.storage_string, self.asset_type.type_of_asset, self.name])

    @property
    def storage_string(self):
        parent_storage = super(InterviewAsset, self).storage_string
        this_storage = asset_helpers.generate_heritage_interview_asset_storage_string(self.interview)
        return '/'.join([parent_storage, this_storage])

    @property
    def source_url(self):
        return reverse("heritage:interview-detail", args=[self.interview.id])

    @property
    def source_string(self):
        return str(self.interview)

    def get_absolute_url(self):
        return reverse('heritage:interview-secureasset-detail', args=[self.interview.id, self.id])

    class Meta:
        verbose_name = "Heritage Interview File"


class SessionAsset(HeritageAsset):
    session = models.ForeignKey(Session)

    def __str__(self):
        return " - ".join([self.storage_string, self.asset_type.type_of_asset, self.name])

    @property
    def storage_string(self):
        parent_storage = super(SessionAsset, self).storage_string
        this_storage = asset_helpers.generate_heritage_session_asset_storage_string(self.session)
        return '/'.join([parent_storage, this_storage])

    @property
    def source_url(self):
        return reverse("heritage:interview-detail", args=[self.session.interview.id])

    @property
    def source_string(self):
        return str(self.session)

    def get_absolute_url(self):
        return reverse('heritage:session-secureasset-detail', args=[self.session.id, self.id])

    class Meta:
        verbose_name = "Heritage Session File"
