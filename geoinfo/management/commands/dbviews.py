import logging
from django.core.management.base import BaseCommand, CommandError
from django.db.models.functions import Concat
from django.db.models import F, Value, CharField

from geoinfo.models import GISLayer, DBView, GISFeaturePolygon, GISFeatureLine, GISFeaturePoint
from development.models import DevelopmentGISLayer, DevelopmentProject
from heritage.models import Place
from geoinfo.utils import dbviews

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


class Command(BaseCommand):
    help = 'Manage database views for geoinfo.  By default this command generates potentially up to 3 new views for each GIS layer, one for' \
           'each geom type (if features of that type are present) point, line, and polygon. Can can be used to delete/rebuild existing ' \
           'all database views as well.'

    def __init__(self, stdout=None, stderr=None, no_color=False):
        super(Command, self).__init__(stdout, stderr, no_color)

    def add_arguments(self, parser):

        # Some optional named tags
        parser.add_argument('--purge', action='store_true', dest='purge', default=False,
                            help='Deletes all GIS layer database views (instances and actual views).')

        parser.add_argument('--rebuild', action='store_true', dest='rebuild', default=False,
                            help='Deletes GIS layer database views (instances and actual views) and recreates them.')

        parser.add_argument('--misc', action='store_true', dest='misc', default=False,
                            help='Runs operation on MISC GIS Layers.')

        parser.add_argument('--development-master', action='store_true', dest='development-master', default=False,
                            help='Runs operation on Development GIS Layers.')

        parser.add_argument('--places', action='store_true', dest='places', default=False,
                            help='Runs operation on Places.')

    def handle(self, *args, **options):
        '''
        Todo: Refactor the options object so it's class-level.
        :param args:
        :param options:
        :return:
        '''
        layers_qs = None

        if options['misc']:
            layers_qs = GISLayer.objects.all()
            if options['purge']:
                self.purge(layers_qs)
            elif options['rebuild']:
                self.purge(layers_qs)
                self.create(layers_qs)
            else:
                logger.info("--misc without purge or rebuild. Exiting.")

        elif options['development-master']:
            if options['purge']:
                self.purge_development()
            elif options['rebuild']:
                self.purge_development()
                self.create_development()
            else:
                logger.info("--development-master without purge or rebuild. Exiting.")
        elif options['places']:
            if options['purge']:
                self.purge_places()
            elif options['rebuild']:
                self.purge_places()
                self.create_places()
            else:
                logger.info("--places without purge or rebuild. Exiting.")
        else:
            logger.info("Requires --misc, --development-master, or --places argument. Exiting.")
            return

    def purge(self, layers_qs):
        count = 0
        # count = DBView.objects.count()
        # DBView.objects.purge()
        for layer in layers_qs:
            count += DBView.objects.drop_related_dbviews(layer)
        logger.info("Successfully deleted {} DBView instances and their related database views".format(count))

    def create(self, layer_queryset):
        for layer in layer_queryset:
            # points:
            if GISFeaturePoint.objects.filter(layer=layer).count() > 0:
                name = str(layer.name).strip() + "_point"
                dbv = DBView.objects.create_related_dbview(
                    layer,
                    name,
                    GISFeaturePoint.objects.filter(layer=layer)
                    )
                logger.info("Successfully generated database view:{}".format(name))
                dbviews.grant_view_perms_to_users(name)

            # polygons
            if GISFeaturePolygon.objects.filter(layer=layer).count() > 0:
                name = str(layer.name).strip() + "_polygon"
                dbv = DBView.objects.create_related_dbview(
                    layer,
                    name,
                    GISFeaturePolygon.objects.filter(layer=layer))
                logger.info("Successfully generated database view:{}".format(name))
                dbviews.grant_view_perms_to_users(name)

            # lines
            if GISFeatureLine.objects.filter(layer=layer).count() > 0:
                name = str(layer.name).strip() + "_line"
                dbv = DBView.objects.create_related_dbview(
                    layer,
                    name,
                    GISFeatureLine.objects.filter(layer=layer))
                logger.info("Successfully generated database view:{}".format(name))
                dbviews.grant_view_perms_to_users(name)

        logger.info("Successfully generated {} database views.".format(DBView.objects.count()))

    def create_development(self):
        '''
        Creates master dbviews for the development project gis layer types (each type holds all features of that type)
        NOTE: This will produce HSTORE errors when if creates the DBView - just ignore.
        :param devt_layer_queryset:
        :return:
        '''
        logger.info('creating for dev')

        values_to_query = [
            'layer__developmentgislayer__name',
            # 'layer__developmentgislayer__project__cedar_project_code',
            'layer__developmentgislayer__project__cedar_project_name',
            'layer__developmentgislayer__project__initial_date',
            'layer__developmentgislayer__project__consultation_stage__stage_name',
            'layer__developmentgislayer__project__status',
            'geometry'
        ]

        viewname_prefix = 'development_'

        viewname_polygon = viewname_prefix + 'polygon'
        viewname_point = viewname_prefix + 'point'
        viewname_line = viewname_prefix + 'line'

        '''
        Use extra to cast the geometry column (typ GEOGRAPHY) to GEOMETRY for ArcGIS
        If we do this then we start getting duplicates in the PostGIS Add Layer dialog.
        The solution for duplicates seem to be to cast to a specific geometry type (Multipolygon,
        Point, Linestring). Can we be guaranteed of those types? I got errors doing straight Polygons.
        The other options is direct user to the Add Vector Layer dialog and connect to PostGIS there;
        for whatever reason it does not have the issue with duplicates appearing.

        See: http://gis.stackexchange.com/questions/185324/duplicate-entries-in-table-list-when-adding-postgis-layer-in-qgis


        Add an "id" field to the views so that users have an obvious choice for pk when adding to QGIS:
            .annotate(feature_id=F('gisfeature_ptr_id'))

        Need to annotate with cedar project code now that it's not actually a field anymore.
            Get the prefix:
            Append to the project id:
            EG not used: cedar_project_code=Concat(F('model__user_first_name'), Value(' '), F('model__user_last_name'), output_field=CharField())
            
        ADDING ADDITIONAL FIELDS:
        You have the choice of adding an entry into "values_to_query" above (preferred method). If you want the field to appear in the view 
         under a different name then don't put it in values_to_query, instead, append another ".annotate()" to each geom type's queryset.
        '''

        # Build project code query:
        default_prefix_instance = DevelopmentProject.get_project_code_prefix()

        select_geog_to_geom_polygon = 'geometry::Geometry(Multipolygon, 4326)'
        select_geog_to_geom_line = 'geometry::Geometry(MultiLineString, 4326)'
        select_geog_to_geom_point = 'geometry::Geometry(Point, 4326)'   # This should be MultiPoint, but the model is only Point.

        layer_query = DevelopmentGISLayer.objects.all()

        '''
        POLYGONS
        '''
        DBView.objects.create_db_view(
            viewname=viewname_polygon,
            queryset=GISFeaturePolygon.objects
                .filter(layer__in=layer_query)
                .extra(select={
                    'geometry': select_geog_to_geom_polygon,
                })
                .values(*values_to_query)
                .annotate(feature_id=F('gisfeature_ptr_id'))    # add feature_id field
                .annotate(cedar_project_code=Concat(Value("'{}'".format(default_prefix_instance)), F('layer__developmentgislayer__project__id'),
                                                    output_field=CharField()))
                .annotate(filing_code=F('layer__developmentgislayer__project__filing_code__label'))
                .filter(layer__developmentgislayer__project__id__isnull=False)
        )
        logger.info("Successfully generated database view:{}".format(viewname_polygon))

        '''
        POINTS
        '''
        DBView.objects.create_db_view(
            viewname=viewname_point,
            queryset=GISFeaturePoint.objects
                .filter(layer__in=layer_query)
                .extra(select={
                    'geometry': select_geog_to_geom_point
                })
                .values(*values_to_query)
                .annotate(feature_id=F('gisfeature_ptr_id'))  # add feature_id field
                .annotate(cedar_project_code=Concat(Value("'{}'".format(default_prefix_instance)), F('layer__developmentgislayer__project__id'),
                                                    output_field=CharField()))
                .annotate(filing_code=F('layer__developmentgislayer__project__filing_code__label'))
                .filter(layer__developmentgislayer__project__id__isnull=False)
        )
        logger.info("Successfully generated database view:{}".format(viewname_point))

        '''
        LINES
        '''
        DBView.objects.create_db_view(
            viewname=viewname_line,
            queryset=GISFeatureLine.objects
                .filter(layer__in=layer_query)
                .extra(select={
                    'geometry': select_geog_to_geom_line
                })
                .values(*values_to_query)
                .annotate(feature_id=F('gisfeature_ptr_id'))  # add feature_id field
                .annotate(cedar_project_code=Concat(Value("'{}'".format(default_prefix_instance)), F('layer__developmentgislayer__project__id'),
                                                    output_field=CharField()))
                .annotate(filing_code=F('layer__developmentgislayer__project__filing_code__label'))
                .filter(layer__developmentgislayer__project__id__isnull=False)
        )
        logger.info("Successfully generated database view:{}".format(viewname_line))

        dbviews.grant_view_perms_to_users(viewname_polygon)
        dbviews.grant_view_perms_to_users(viewname_line)
        dbviews.grant_view_perms_to_users(viewname_point)

    def purge_development(self):
        viewname_prefix = 'development_'
        viewname_polygon = viewname_prefix + 'polygon'
        viewname_point = viewname_prefix + 'point'
        viewname_line = viewname_prefix + 'line'

        DBView.objects.drop_db_views([viewname_line, viewname_point, viewname_polygon])

    def create_places(self):
        """
        Uses ST_CollectionExtract to parse out the mixed geometry types and sets those into 
        separate views. ST_CollectionExtract seems to set NULL the geometries that don't match
        the selected type. We need to check against ST_IsEmpty to filter those rows out of the views.
        :return: 
        """
        logger.info('creating for places')

        # see dev for more examples
        values_to_query = [
            'name',
            'geometry'
        ]

        viewname_prefix = 'places_'

        viewname_polygon = viewname_prefix + 'polygon'
        viewname_point = viewname_prefix + 'point'
        viewname_line = viewname_prefix + 'line'

        select_geog_to_geom_polygon = 'ST_CollectionExtract(geometry, 3)::Geometry(Multipolygon, 4326)'
        select_geog_to_geom_line = 'ST_CollectionExtract(geometry, 2)::Geometry(MultiLineString, 4326)'
        select_geog_to_geom_point = 'ST_CollectionExtract(geometry, 1)::Geometry(MultiPoint, 4326)'

        place_query = Place.objects.all()

        '''
        POLYGONS
        '''
        DBView.objects.create_db_view(
            viewname=viewname_polygon,
            queryset=place_query
                .extra(select={
                'geometry': select_geog_to_geom_polygon,
            })
                .values(*values_to_query)
                .annotate(feature_id=F('id'))  # add feature_id field
        )
        logger.info("Successfully generated database view:{}".format(viewname_polygon))

        '''
        LINES
        '''
        DBView.objects.create_db_view(
            viewname=viewname_line,
            queryset=place_query
                .extra(select={
                'geometry': select_geog_to_geom_line,
            })
                .values(*values_to_query)
                .annotate(feature_id=F('id'))  # add feature_id field
        )
        logger.info("Successfully generated database view:{}".format(viewname_line))

        '''
        POINTS
        '''
        DBView.objects.create_db_view(
            viewname=viewname_point,
            queryset=place_query
                .extra(select={
                'geometry': select_geog_to_geom_point,
            })
                .values(*values_to_query)
                .annotate(feature_id=F('id'))  # add feature_id field
        )
        logger.info("Successfully generated database view:{}".format(viewname_point))

        dbviews.grant_view_perms_to_users(viewname_polygon)
        dbviews.grant_view_perms_to_users(viewname_line)
        dbviews.grant_view_perms_to_users(viewname_point)

    def purge_places(self):
        viewname_prefix = 'places_'
        viewname_polygon = viewname_prefix + 'polygon'
        viewname_point = viewname_prefix + 'point'
        viewname_line = viewname_prefix + 'line'

        DBView.objects.drop_db_views([viewname_line, viewname_point, viewname_polygon])
