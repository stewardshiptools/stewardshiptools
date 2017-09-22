import logging
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.contrib.gis.db import models
from django.contrib.gis.db.models.query import GeoQuerySet
from model_utils.managers import InheritanceManager, InheritanceManagerMixin, InheritanceQuerySetMixin
from django_hstore import hstore
from django.core.urlresolvers import reverse
from cryptographic_fields.fields import EncryptedCharField

from django.db import connection
from django.db.models import Model
from django.db.utils import ProgrammingError

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class InheritanceHStoreGeoManager(InheritanceManagerMixin, hstore.HStoreGeoManager):
    pass


class InheritanceGeoQuerySet(InheritanceQuerySetMixin, GeoQuerySet):
    """
    We can add custom 'shortcut' queries here.
    """
    pass


class GISLayerMaster(models.Model):
    '''
    This is the GISLayer super class - inherited by all C8 apps' gis layers.
    '''
    input_type_choices = (
        ('wkt', 'WKT'),
        ('map', 'Draw on a map'),
        ('file', 'File'),
        ('geomark', 'Geomark'),
        ('wfs', 'WFS GeoJSON'),
        ('custom', 'Custom')
    )
    layer_type_value = 'master'  # This should never show up.

    machine_name = models.CharField(max_length=200, unique=True, blank=True, null=True)
    layer_type = models.CharField(max_length=100, default='', blank=True, null=True)
    name = models.CharField(max_length=200)
    input_type = models.CharField(max_length=50, choices=input_type_choices, default='wkt')
    wkt = models.TextField(blank=True, null=True)
    draw = models.GeometryCollectionField(srid=4326, blank=True, null=True)
    feature_titles_template = models.CharField(max_length=200, blank=True, null=True,
                                               help_text='If you know the column headers in your attributes table you '
                                                         'can provide a title template here.  Wrap column names in '
                                                         'percent signs (e.g. My layer feature %ID% %poly name%) '
                                                         'Some additional features can also be accessed by '
                                                         'surrounding parts of the template with pound signs. '
                                                         'Currently available is #seq# which provides the feature\'s '
                                                         'place in the sequence of features being generated.'
                                               )
    file = models.FileField(upload_to='geoinfo', blank=True, null=True)
    geomark = models.CharField(max_length=2083, blank=True, null=True)

    # WGS Geojson fields.  Takes a url and optional information about periodically refreshing the data.
    wfs_geojson = models.URLField('WFS GeoJSON URL', max_length=2083, blank=True, null=True,
                                  help_text="Please enter a url that resolves as WFS formatted GeoJSON")
    wfs_username = models.CharField(max_length=200, blank=True, null=True)
    wfs_password = EncryptedCharField(max_length=200, blank=True, null=True)

    number_of_points = models.IntegerField(blank=True, null=True)
    number_of_lines = models.IntegerField(blank=True, null=True)
    number_of_polygons = models.IntegerField(blank=True, null=True)
    polygons_combined_area = models.FloatField(blank=True, null=True)  # In meters

    reload_features = models.BooleanField(default=False)

    notes = models.TextField(blank=True, null=True)
    author = models.ForeignKey(User, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    extra_info = hstore.DictionaryField(blank=True, null=True)

    polygon_style = models.ForeignKey('maps.StylePolygon', blank=True, null=True)
    polyline_style = models.ForeignKey('maps.StylePolyline', blank=True, null=True)
    point_style = models.ForeignKey('maps.StyleCircle', blank=True, null=True)

    objects = InheritanceManager()

    def __str__(self):
        return self.name

    def __init__(self, *args, **kwargs):
        super(GISLayerMaster, self).__init__(*args, **kwargs)
        self.__original_fields = {
            'input_type': self.input_type,
            'wkt': self.wkt,
            'draw': self.draw,
            'file': self.file,
            'feature_titles_template': self.feature_titles_template,
            'geomark': self.geomark,
            'wfs_geojson': self.wfs_geojson
        }

    def save(self, *args, **kwargs):
        self.layer_type = self.layer_type_value
        stats = self._calculate_stats()

        # If the calculated stats differ from the stored stats OR this is a new intance, calculate stats.
        # I WAS saving so that features would be created and then calculating stats and saving AGAIN.
        # However, that broke saving layers in code.
        # TODO Change this so that we calculate and cache stats on the fly.
        if self.id is not None or \
                stats['point_count'] != self.number_of_points or \
                stats['line_count'] != self.number_of_lines or \
                stats['polygon_count'] != self.number_of_polygons or \
                stats['polygon_area'] != self.polygons_combined_area:
            self.number_of_points = stats['point_count']
            self.number_of_lines = stats['line_count']
            self.number_of_polygons = stats['polygon_count']
            self.polygons_combined_area = stats['polygon_area']

        super(GISLayerMaster, self).save(*args, **kwargs)

    @property
    def get_stats(self):
        return {
            'point_count': self.number_of_points,
            'line_count': self.number_of_lines,
            'polygon_count': self.number_of_polygons,
            'polygon_area': self.polygons_combined_area
        }

    def _calculate_stats(self):
        point_features = GISFeaturePoint.objects.filter(layer=self)
        point_count = point_features.count()

        line_features = GISFeatureLine.objects.filter(layer=self)
        line_count = line_features.count()

        polygon_features = GISFeaturePolygon.objects.filter(layer=self)
        polygon_count = polygon_features.count()
        polygon_area = 0

        polygonset = polygon_features.area()

        for poly in polygonset:
            polygon_area += poly.area.sq_m

        stats = {
            'point_count': point_count,
            'line_count': line_count,
            'polygon_count': polygon_count,
            'polygon_area': polygon_area,
        }

        return stats

    @property
    def layer_type_value(self):
        '''
        Gets the value to be saved into the layer_type field when the
        model's save method is called.
        :return:
        '''
        return 'master'


class GISLayer(GISLayerMaster):
    '''
    This is the general MISC GIS Layer class. For Misc layers that do not
    belong to any particular app and live only in Spatial Tools.
    '''
    layer_type_value = 'Misc.'
    objects = InheritanceManager()

    class Meta:
        verbose_name = 'Misc. Layer'
        verbose_name_plural = 'Misc. Layers'

    def get_absolute_url(self):
        return reverse('geoinfo:layer-detail', kwargs={'pk': self.pk})

    def get_edit_url(self):
        return reverse('geoinfo:layer-update', kwargs={'pk': self.pk})

    def get_delete_url(self):
        return reverse('geoinfo:layer-delete', kwargs={'pk': self.pk})

    def __str__(self):
        return "(GEN-M) {}".format(self.name)


class GISFeature(models.Model):
    name = models.CharField(max_length=200)
    layer = models.ForeignKey('GISLayerMaster')
    image = models.ImageField(upload_to='geoinfo-images', blank=True, null=True)
    data = hstore.DictionaryField(blank=True, null=True)

    extra_info = hstore.DictionaryField(blank=True, null=True)  # Extra info that need not be displayed.

    objects = InheritanceHStoreGeoManager()

    def __str__(self):
        return self.name


class GISFeaturePoint(GISFeature):
    geometry = models.PointField(geography=True)

    objects = models.GeoManager()

    @property
    def map_style(self):
        return self.layer.point_style


class GISFeatureLine(GISFeature):
    geometry = models.MultiLineStringField(geography=True)

    objects = models.GeoManager()

    @property
    def map_style(self):
        return self.layer.polyline_style


class GISFeaturePolygon(GISFeature):
    geometry = models.MultiPolygonField(geography=True)

    objects = models.GeoManager()

    @property
    def map_style(self):
        return self.layer.polygon_style


class SpatialReportMaster(models.Model):
    name = models.CharField(max_length=200)
    distance_cap = models.CharField(max_length= 50, help_text='Enter a distance in meters (m) or kilometers (km).'
                                                              'The report will only show hits that are within this'
                                                              'distance.', default='5km')

    def __str__(self):
        return self.name

    class Meta:
        abstract = True


class SpatialReport(SpatialReportMaster):
    """ A generic implementation of spatial reports.
    """
    report_on = models.ManyToManyField('GISLayerMaster', related_name='layers_reported_on', blank=True)

    def get_absolute_url(self):
        return reverse('geoinfo:spatialreport-detail', kwargs={'pk': self.pk})


class SpatialReportItem(models.Model):
    report = models.ForeignKey('SpatialReport')
    distance_cap = models.CharField(max_length= 50, help_text='Enter a distance in meters (m) or kilometers (km).'
                                                              'The report will only show hits that are within this'
                                                              'distance.  This value overrides the value given in the'
                                                              'overall Spatial Report.', blank=True, null=True)
    layer = models.ForeignKey('GISLayerMaster', related_name='spatialreport_items')


class DBViewManager(models.Manager):
    """
    Database Views Models & Manager.
        - the purpose of a related database view, ie a DBView, is so that views can be created in the
            database and then are tracked by some model instance, eg GISLayer. Why not just have a text field
            with the view name? That's boring. Also, GISLayers can potentially have up to three views (one for
            each geometry type), which gets easier to manage if there is some relation.

        - follow-up work:
            - create_db_view assumes that the viewname string has already been sanitized (ie. input by user/script
                in GISLayer name. Layer is saved, then name is used to create the view.
            - signals could be added that handle the database view drops, so we wouldn't need to run custom
                object manager methods.
        - notes: there is a subtle yet significant difference in method names. In retrospect, the
                naming was a little close for comfort.
            - "dbview" -- refers to a DBView model instance.
            - "db_view" -- refers to an actual view in the database.


        - useage:
            - create a view in the database and relate it to a model instance:
                DBView.objects.create_related_dbview(<model_instance>, <viewname>, <queryset>)
                - note: this can be repeated, one instance can have many related database views.
            - create a view in the database that is not related to a model instance:
                DBView.objects.create_db_view(<viewname>, <queryset>
            - delete a related view instance and drop all of its corresponding database views:
                DBView.objects.drop_related_dbviews(<instance>)
            - delete a view(s) in the database that is not related to a model instance:
                DBView.objects.drop_db_views(<[names]>)

    """
    def create_related_dbview(self, instance, viewname, queryset=None):
        '''
        Creates a DBView object and a proper view in the database.
        :param instance: the object instance to which the view will be related.
        :param viewname: the name the view will have in the db
        :param queryset: the queryset that will be turned into a view. If one
        isn't supplied, a queryset will be made from the object instance.
        :return:
        '''

        if not isinstance(instance, Model):
            raise TypeError('''Error in create_related_dbview. Supplied instance is not a model. Did you
                give it a queryset by mistake?''')

        # make a queryset from the related_object's id if one wasn't supplied:
        if queryset is None:
            queryset = instance.__class__.objects.filter(id=instance.id)

        unique_view_name, sql = self.create_db_view(viewname, queryset)
        if unique_view_name is not None:
            dbview = self.create(
                obj=instance,
                viewname=unique_view_name,
                definition=sql,
            )
            return dbview
        else:
            raise ProgrammingError("Could not create view:", viewname, " sql:", sql)

    def create_db_view(self, viewname, queryset):
        '''
        Creates only a view in the database, not a DBView object.
        :param viewname: the name the view will have in the db
        :param queryset: the queryset that will be turned into a view
        :return: the name that the view was saved with -- it will check for
        uniqueness before saving.
        '''
        queryset = self.alias_hstore_fields(queryset)

        # save the sql string:
        sql = queryset.query.__str__()

        # TODO - Fix SQL Injection Vulnerability -- VIEWNAME!!!
        # Do a cheap fix on the input viewname. Add more to the list.
        for x in [';', '"']:
            viewname = viewname.replace(x, '')
        unique_view_name = self.get_available_view_name(viewname)

        try:
            # Execute create view on database:
            create_view_str = 'CREATE VIEW "{}" AS {}'.format(unique_view_name, sql)
            cursor = connection.cursor()
            cursor.execute(create_view_str)
            return unique_view_name, sql
        except ProgrammingError as err:
            logger.error("Error creating db view: {}. {}".format(unique_view_name, str(err)))
            return None, sql

    def drop_related_dbviews(self, instance):
        '''
        Drops and DBView and database views that are related to instance.
        :param instance: object instance that is related to DBView objects
        :return:
        '''
        ct = ContentType.objects.get_for_model(instance)

        names = DBView.objects.filter(
            content_type=ct,
            object_id=instance.id
        ).values_list("viewname", flat=True)

        logger.info("Dropping views: {}".format(" ".join(names)))

        # Execute drop view on database:
        self.drop_db_views(names)

        DBView.objects.filter(
            content_type=ct,
            object_id=instance.id
        ).delete()

        return len(names)

    def drop_db_views(self, names):
        '''
        :param names: list of database view names to be dropped.
        :return:
        '''
        # DBView.objects.all().values_list("viewname", flat=True)
        for name in names:
            try:
                drop_view_str = 'DROP VIEW "{}";'.format(name)
                cursor = connection.cursor()
                cursor.execute(drop_view_str)
            except ProgrammingError as err:
                # there was an error dropping the view.
                logger.error("Error dropping database view: {}. {}".format(name, str(err)))

    def get_related_dbviews(self, instance):
        '''
        :param instance:
        :return: filtered queryset of DBView objects that are related to instance.
        '''
        ct = ContentType.objects.get_for_model(instance)
        return DBView.objects.filter(
            content_type=ct,
            object_id=instance.id
        )

    def get_db_view_names(self):
        '''
        Used to make sure we don't try to create a new view with an existing view name
        :return: list of viewnames directly from the database.
        '''
        query_views = '''
            select viewname from pg_catalog.pg_views
            where schemaname NOT IN ('pg_catalog', 'information_schema')
            order by schemaname, viewname;
        '''
        cursor = connection.cursor()
        cursor.execute(query_views)
        viewnames = [n[0] for n in cursor.fetchall()]
        return viewnames

    def get_available_view_name(self, name):
        '''
        Checks DBViews and real db views to see if the name already exists. Increments
        the name if it does.
        :param name:
        :return: available view name -- adds "_#" if another view with that name exists.
        '''
        not_unique = True
        new_name = name
        counter = 0

        # combine view names from DBViews and actual database views to check for uniqueness:
        names = self.get_db_view_names()
        names.extend(DBView.objects.all().values_list("viewname", flat=True))
        names = set(names)

        while not_unique:
            counter += 1
            if new_name in names:
                new_name = name + "_{}".format(counter)
                continue
            else:
                return new_name

    def get_hstore_subfield_names(self, queryset):
        '''
        :param queryset:
        :return: dict of hstore fields and subfields.
        Note: if the queryset is empty you will get no hstore key fields in your view. So populate it first.
        '''

        # You can alias an other fields with this:
        # queryset = queryset.extra(
        #     select={
        #         'ALIAS': 'FIELDNAME'
        #     }
        # )

        h_store_fields = {}
        first = queryset.first()  # Needed in case there is an hstore field.

        for field in queryset.model._meta.get_fields():
            # print ("field name:", field.name, " - field type:", field.__class__)

            if field.__class__ is hstore.DictionaryField or field is hstore.SerializedDictionaryField:
                # use the first record and build hstore key list off that.
                # Note: if the queryset is empty you will get no hstore key fields in your view. So populate it first.
                try:
                    h_store_fields[field.name] = getattr(first, field.name, None).keys()  # get the hstore fieldnames
                except AttributeError as err:
                    logger.warning("Error extracting hstore attribute for field: {}. {}".format(str(field), str(err)))

        return h_store_fields

    def alias_hstore_fields(self, queryset):
        '''
        :param queryset:
        :return: queryset
        '''

        # Pull out the hstore fields and subfields:
        h_store_fields = self.get_hstore_subfield_names(queryset)
        h_split_query_template = '{0} -> \'{1}\''

        # Build sql for aliasing the hstore fields:
        for hstore_fieldname in h_store_fields.keys():
            for subfield in h_store_fields[hstore_fieldname]:
                queryset = queryset.extra(
                    select={
                        hstore_fieldname + '_' + subfield: h_split_query_template.format(hstore_fieldname, subfield)
                    }
                ).defer(hstore_fieldname)  # Hide the hstore data field
        return queryset

    def purge(self):
        '''
        Self destruct. Deletes all DBVs and database views
        :return:
        '''
        names = DBView.objects.all().values_list("viewname", flat=True)
        self.drop_db_views(names)
        DBView.objects.all().delete()


class DBView(models.Model):
    """
    The database view (DBView) model class. Works with DBViewManager.
    """

    viewname = models.CharField(max_length=100, blank=False, null=False)
    definition = models.TextField(blank=False, null=False)

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    obj = GenericForeignKey('content_type', 'object_id')

    objects = DBViewManager()

    def __str__(self):
        return self.viewname
