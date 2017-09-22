import magic
import zipfile
import tempfile
import shutil
import re
import logging
import requests

from django.contrib.gis.geos import GEOSGeometry, MultiLineString, MultiPolygon, WKBWriter, Point
from django.contrib.gis.gdal import DataSource, GDALException
from django.contrib.gis.gdal.srs import SpatialReference, CoordTransform
from django.contrib.gis.gdal.feature import Feature

from django.contrib.gis.db.models import GeometryField
from django.db.models.functions import Coalesce
from django.db.models import Value, F, Func

from django.db import connection

from geoinfo.models import GISFeaturePoint, GISFeatureLine, GISFeaturePolygon, GISFeature
from geoinfo.utils.geomark import Geomark
from geoinfo.functions import CastGeometry

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class GeomParser:
    '''
    Use the GeomParse to parse a GISMasterLayer's datasource into GISFeature instances.
    It needs a saved GISLayerMaster instance.
    Instantiate with a GISLayerMaster instance and call process_geoinfo_to_layer().
    If you are adding a format note the following:
        - the datatype must be checked for and prepared in the _prepare() method.
        - the datatype should get it's own _prepare_X() method.
        - the _prepare_X() method must produce a gdal Datasource-readable object.
        - the _prepare_X() method must call _parse_datasource() with the prepared datasource.
        - the rest is magic.
    '''
    def __init__(self, obj=None, datasource=None, input_type=None):
        '''

        :param obj: A GISLayer instance
        :param datasource: some sort of geometry source.  Currently WKT, and OGR compliant files are supported.
        :param input_type: The type of datasource.  One of: wkt, file
        '''
        self.gislayer = obj
        if obj:
            self.type = obj.input_type
        else:
            self.type = input_type

        # Populate self.datasource
        if datasource is not None and input_type is not None and obj is None:
            self.datasource = datasource

        # Last of all, _prepare an empty list to store geoms.
        self.features = []

        self.title_template = None
        self.curr_feature = None
        self.i = 0
        self.skip = False

    def process_geoinfo_to_layer(self):
        '''
        Parses geometries and features out of a datasource, and generates GISFeatures.  Requires a GISLayer object.
        :param obj: A GISLayer object to replace the original, or add one if there wasn't one provided.
        :return: True on success, False on failure.
        '''
        self._prepare()
        assert self.gislayer is not None

        return self._generate_gisfeatures()

    def _prepare(self):
        # Add additional protocols to this else/if and add a new method to populate geoms out of it.
        if self.type == 'wkt':
            self._prepare_wkt()
        elif self.type == 'map':
            self._prepare_map()
        elif self.type == 'file':
            self._prepare_file()  # Returns False on failure
        elif self.type == 'geomark':
            self._prepare_geomark()  # Returns False on failure
        elif self.type == 'wfs':
            self._prepare_wfs()  # Returns False on failure
        else:
            # Set the skip flag and do nothing
            self.skip = True
            return

    def _prepare_wkt(self):
        if self.gislayer:
            self.datasource = self.gislayer.wkt

        if self.datasource:
            self.datasource = GEOSGeometry(self.datasource)
            # self.prepare_geos(self.datasource)
            self._parse_datasource(self.datasource.geojson)

    def _prepare_map(self):
        '''
        Prepares a datasource for features draw on the map.
        :return:
        '''
        if self.gislayer and self.type == 'map':  # Technically there most be a GISLayer object for this to happen...
            self.datasource = self.gislayer.draw

        # self.prepare_geos(self.datasource)
        self._parse_datasource(self.datasource.geojson)

    def _prepare_file(self):
        '''
        Prepare a datasource from an uploaded file - currently KMZ, KML, SHPZ, others?
         The unzipping code should be refactored into a separate method.
        :return:
        '''
        if self.gislayer:
            self.datasource = self.gislayer.file

            self.title_template = self.gislayer.feature_titles_template

        filename_pattern = re.compile('^(.+).(shp|kml)$')  # We only care about shps and kml... For now.
        file = self.datasource

        if not file:
            # TODO return some sort of error message here.
            return False

        content_type = magic.from_file(file.path, mime=True)

        # If the file needs extracted.
        if content_type == b'application/zip':
            filepath = file.name.split('/')
            filename = filepath[-1]
            # Copy to /tmp/
            # ... create a randomly generated dir in /tmp
            with tempfile.TemporaryDirectory() as tmpdir:
                # Move the uploaded file to /tmp for safe extraction...
                tmp_zip = "%s/%s" % (tmpdir, filename)
                shutil.copyfile(file.path, tmp_zip)

                # Extract the zip and save names of files.
                with zipfile.ZipFile(tmp_zip) as zf:
                    zf.extractall(tmpdir)
                    for member in zf.infolist():  # TODO Complain about multiple layers.  Still do it though.
                        match = filename_pattern.match(member.filename)
                        if match:
                            layer_name = match.group(1)
                            shp_path = "%s/%s.%s" % (tmpdir, layer_name, match.group(2))
                            return self._parse_datasource(shp_path)

        else:
            # If not a zipped archive attempt to feed the file directly to DataSource()
            return self._parse_datasource(file.path)

    def _prepare_geomark(self):
        '''
        Prepare geomark datasource
        :return:
        '''
        if self.gislayer:
            self.datasource = self.gislayer.geomark  # In this case, the datasource is a geomark id or url.

        if self.datasource:
            geomark = Geomark(self.datasource)
            response = geomark.get_response("parts", "geojson")
            if response.status_code == 200:  # If it isn't 200 an exception should be raised anyways, but... meh
                geojson = response.text
                return self._parse_datasource(geojson)

    def _prepare_wfs(self):
        '''
        Prepare geomark datasource
        :return:
        '''
        if self.gislayer:
            self.datasource = self.gislayer.wfs_geojson  # In this case, the datasource is a geomark id or url.
            self.title_template = self.gislayer.feature_titles_template

        if self.datasource:
            rq_kwargs = {
                'headers': {'Accept': 'application/json'}
            }

            # HTTP Basic auth...  This might need some updating in the future if more complicated auth is faced.
            if self.gislayer.wfs_username and self.gislayer.wfs_password:
                rq_kwargs['auth'] = (self.gislayer.wfs_username, self.gislayer.wfs_password)

            response = requests.get(self.datasource, **rq_kwargs)
            if response.status_code == 200:  # If it isn't 200 an exception should be raised anyways, but... meh
                geojson = response.text
                return self._parse_datasource(geojson)

    def _parse_datasource(self, datasource):
        try:
            ds = DataSource(datasource)

            # gather the features from the datasource, and fix the geom types on the first pass.
            # feats actually should contain a list a sublists, each sublist is: [gdal_feature, geos_geom]
            # done this way so that exploded geoms get to keep a copy of the gdal_feature fields for saving
            # into a GISFeature.
            feats = []
            for layer in ds:
                for gdal_feature in layer:

                    # clean up the feature
                    try:
                        geos_geom_fixed = self._fix_and_explode(gdal_feature)

                        # geos_geom may actually be a list (eg MultiPoint >> Points), so
                        # extend feats with a list of lists:
                        if isinstance(geos_geom_fixed, list):
                            feats.extend([[gdal_feature, sub_geom] for sub_geom in geos_geom_fixed])
                        else:
                            feats.extend([[gdal_feature, geos_geom_fixed]])

                    except GDALException as e:
                        logger.error("Exception encountered parsing datasource: \"{}\"".format(str(e)))
                        # return False

            # go over features, look for bad geoms, and set srid.
            # remember, the gdal_feature geometry should be ignored, use the second list item (the geos_geometry)
            '''
            for i in range(0, len(feats)):
                try:
                    # feat = feats[i][0]
                    feat_geom = feats[i][1]  # work on geos geometry
                    if feat_geom.srid != 4326:
                        feat_geom.transform(4326)
                    if not feat_geom.valid:
                        feat_geom = postgis_makevalid(feat_geom)
                        feats[i][1] = feat_geom

                except GDALException as e:
                    logger.debug(
                        "Bad geom (i={}) generating features from layer \"{}\" id: {} . Exception: {}".format(i, self.gislayer.name, self.gislayer.id,
                                                                                                              str(e)))

                    # If we can't manage to make the geom good, then set the feature to None and we'll filter it out.
                    feats[i] = None

            # Filter out None'd features and save for generating gisfeatures:
            self.features = [feature for feature in feats if feature is not None]
            '''
            self.features = feats

            return True

        except GDALException as e:
            logger.error("Exception encountered parsing datasource: \"{}\"".format(str(e)))
            return False

    def _fix_and_explode(self, feat):
        '''
        Switches geometry types, makes calls to _explode() as needed.
        :param feat: a gdal feature
        :return: either a GEOSGeometry or a list of GEOSGeometries
        '''

        # ditch the feature, we just want the geometry. If this method
        # called recursively after an _explode then feat will be a GEOSGeometry object.
        # We don't always seem to get a GEOSGeometry object from feat.geom. Use .wkb
        # and GEOSGeometry() to create a proper GEOSGeom object. Also, some acrobatics
        # required to get proper srs srid if srid is not defined:
        if isinstance(feat, Feature):
            # try to get the srid from this feature:
            geom = feat.geom    # get clone of feature geometry.
            if geom.srid is not None:
                srid = geom.srid
            else:
                # if we can't get the srid but there IS a defined projection we can transform
                # the geometry to 4326 and use that srid:
                try:
                    ct = CoordTransform(geom.srs, SpatialReference('WGS84'))
                    geom.transform(ct)
                    srid = geom.srid
                except TypeError as e:
                    logger.debug("Could not establish srs of input geometry. Defaulting to 4326.")
                    srid = 4326
            geom = GEOSGeometry(geom.wkb, srid=srid)
        elif isinstance(feat, GEOSGeometry):
            geom = feat  # feat is a GEOSGeometry due to recursive loop
        else:
            raise TypeError ("What type of geometry object is this?: {}".format(feat))

        # Project non-4326 geoms to 4326 and check validity, correct if invalid.
        # This will raise a GDAL Exception if the geom is too messed up.
        # Allow exception to be caught in _parse_datasource() method.
        if geom.srid != 4326:
            geom.transform(4326)
        if not geom.valid:
            # Caution: this is capable of making a bad LINESTRING into a MULTIPOINT.
            geom = postgis_makevalid(geom)

        # remove z-dimension if present:
        geom = self._fix_dims(geom)

        if geom.geom_type == 'GeometryCollection':
            # _explode and re-fix in case sub geometries need fixing.
            return [self._fix_and_explode(g) for g in self._explode(geom)]

        elif geom.geom_type == 'MultiPoint':
            return self._explode(geom)

        elif geom.geom_type == 'LineString':
            return MultiLineString(geom, srid=geom.srid)

        elif geom.geom_type == 'Polygon':
            return MultiPolygon(geom, srid=geom.srid)
        else:
            return geom

    def generate_features_old(self, gislayer=None):
        '''
        Deprecated, kept for reference.
        generates geometries and features from the parsed datasource.  Requires a GISLayer object.
        :param gislayer: A GISLayer object to replace the original, or add one if there wasn't one provided.
        :return: True on success, False on failure.
        '''
        if self.skip:
            return False  # Do nothing

        if gislayer:
            self.gislayer = gislayer

        if not self.gislayer:
            return False  # This method requires a GISLayer object.

        success = False
        i = 1

        logger.debug("Generating features for {}".format(self.gislayer))
        # First... Delete any existing feature...
        self.gislayer.gisfeature_set.all().delete()

        title_pattern = re.compile(r'([#%])([^#%]+)[#%]')

        for feature in self.features:
            success = True
            gdal = False
            try:
                # Prepare the feature objects...
                # if feature.__class__.__name__ == 'Feature':
                if isinstance(feature, Feature):
                    gdal_geom = feature.geom
                    gdal_geom.transform(4326)  # Reproject to WGS84
                    geom = gdal_geom.geos
                    geom = self.sanitize_geom(geom)
                else:
                    geom = feature.geom
            except GDALException as e:
                logger.debug("Bad geom (i={}) generating features from layer \"{}\" id: {} . Exception: {}".format(i, self.gislayer.name, self.gislayer.id, str(e)))
                continue

            geom = feature.geom

            # geom = self._fix_dims(geom)

            geom_type = geom.geom_type

            feature_name = 'Feature #%d generated by "%s"' % (i, self.gislayer.name)

            if self.title_template and self.type == 'file':
                self.curr_feature = feature
                self.i = i

                feature_name, n = title_pattern.subn(self._title_repl, self.title_template)
            elif self.type == 'geomark':
                feature_name = "Feature #%s generated by %s" % (
                    feature.get('id'),
                    self.gislayer.name
                )

            # This is only for geoms.  Attributes are seperate.
            feature_values = {
                'name': feature_name.strip(),
                'layer': self.gislayer,
                'geometry': geom
            }

            gisfeature = None
            if geom_type == 'Point':
                # Create a GISFeaturePoint
                gisfeature = GISFeaturePoint.objects.create(**feature_values)

            elif geom_type in ['LineString', 'MultiLineString']:
                # Create a GISFeatureLine
                gisfeature = GISFeatureLine.objects.create(**feature_values)

            elif geom_type in ['Polygon', 'MultiPolygon']:
                # Create a GISFeaturePolygon
                gisfeature = GISFeaturePolygon.objects.create(**feature_values)

            else:
                # Something has gone horribly wrong!
                raise ValueError("Geom was not and could not be converted to any of the following types: Point,"
                                 "LineString, MultiLineString, Polygon, Multipolygon.")

            # Create attribute containers.
            data = {}
            for field in feature.fields:
                label = field.decode("utf-8")

                # Skip if the attribute has no value for this feature.
                try:
                    val = feature.get(label)
                except KeyError:
                    val = ''

                data[label] = str(val)
                gisfeature.data = data

            gisfeature.save()

            i += 1

        return success

    def _generate_gisfeatures(self):
        '''
        generates geometries and features from the parsed datasource.  Requires a GISLayer object.
        Assumes that _prepare() has been called.
        :param gislayer: A GISLayer object to replace the original, or add one if there wasn't one provided.
        :return: True on success, False on failure.
        '''

        i = 1

        logger.debug("Generating features for {}".format(self.gislayer))

        # First... Delete any existing features...
        self.gislayer.gisfeature_set.all().delete()

        gisfeatures = []
        for feature_pair in self.features:
            gisfeatures.append(self._generate_gisfeature(self.gislayer, i, feature_pair[0], feature_pair[1]))
            i += 1

        # TODO I would love to do a bulk create here instead of doing this one by one, but the django docs say it's not possible on inherited models.
        for gisfeature in gisfeatures:
            gisfeature.save()
        return

    def _generate_gisfeature(self, gislayer, feature_id, gdal_feature, geos_geom):
        logger.debug("Generating feature id:{}".format(feature_id))

        feature_name = self.get_feature_name(feature_id, gdal_feature, gislayer)

        # This is only for geoms.  Attributes are seperate.
        feature_values = {
            'name': feature_name,
            'layer': gislayer,
            'geometry': geos_geom
        }

        model = self._get_gisfeature_model_class(geos_geom.geom_type)
        if model is None:
            # Something has gone horribly wrong!
            raise ValueError("Geom was not and could not be converted to any of the following types: Point,"
                             "LineString, MultiLineString, Polygon, Multipolygon.")
        else:
            gisfeature = model(**feature_values)

        # NOTE TO SELF: Does the gis feature have to be saved first?

        # Create attribute containers.
        data = {}
        for field in gdal_feature.fields:
            label = field.decode("utf-8")

            # Skip if the attribute has no value for this feature.
            try:
                val = gdal_feature.get(label)
            except KeyError:
                val = ''

            data[label] = str(val)
            gisfeature.data = data

        # gisfeature.save()

        # return success
        return gisfeature

    def get_feature_name(self, feature_id, gdal_feature, gislayer):
        title_pattern = re.compile(r'([#%])([^#%]+)[#%]')

        # This seems bonkers to use class-level variables to do this.
        if self.title_template:
            self.curr_feature = gdal_feature
            self.i = feature_id
            feature_name, n = title_pattern.subn(self._title_repl, self.title_template)
        else:
            feature_name = 'Feature #{} generated by "{}"'.format(feature_id, gislayer.name)

        return feature_name.strip()

    def _get_gisfeature_model_class(self, geom_type):
        '''
        Figures out what cedar GISFeature type to use eg GISFeaturePoint, GISFeatureLine, GISFeaturePolygon
        :param geom_type:
        :return: GISFeaturePoint or GISFeatureLine or GISFeaturePolygon or None
        '''
        klass = None
        if geom_type == 'Point':
            # Create a GISFeaturePoint
            klass = GISFeaturePoint

        elif geom_type in ['LineString', 'MultiLineString']:
            # Create a GISFeatureLine
            klass = GISFeatureLine

        elif geom_type in ['Polygon', 'MultiPolygon']:
            # Create a GISFeaturePolygon
            klass = GISFeaturePolygon

        else:
            klass = None

        return klass

    def _explode(self, geom):
        '''
        Returns a list of Features. For now should only be used on MultiPoints and GeometryCollections
        :param feat: a GEOSGeometry object
        :return: a list of single-part GEOSGeometry instances
        '''
        exploded_feats = []
        if geom.geom_type == 'MultiPoint':
            for pair in geom.coords:
                exploded_feats.append(
                    Point(x=pair[0], y=pair[1], z=None, srid=geom.srid)
                )

        elif geom.geom_type == 'GeometryCollection':
            for g in geom:
                exploded_feats.extend(
                    self._explode(g)
                )

        else:
            # logger.debug("_explode multipart called on a non-multipoint feature. Hmm returning feature untouched.")
            return [geom]   # return as a list so we can use this function recursively.

        return exploded_feats

    def _fix_dims(self, geom):
        if geom.hasz:
            wkb_w = WKBWriter()
            wkb_w.srid = True
            wkb_w.outdim = 2
            ewkb = wkb_w.write_hex(geom)
            geom_2d = GEOSGeometry(ewkb)
            return geom_2d
        else:
            return geom

    def _title_repl(self, match):
            '''
            Using self. for these vars is not great.
            :param match:
            :return:
            '''
            if match.group(1) == '#':
                if match.group(2) == 'seq':
                    return str(self.i)

            elif match.group(1) == '%':
                if self.curr_feature is None:
                    return ''

                try:
                    # This needs cast into a string because re.subn hates when it gets numbers.
                    return str(self.curr_feature.get(match.group(2)))
                except KeyError:
                    return ''

            return ''


def postgis_makevalid(geos_geom):
    '''
    Makes use of postgis's ST_MakeValid method to attempt to repair a messed up geometry.
    Maybe this should just be rewritten to fire raw sql with a wkb geom input.
    WARNING: They may change the geometry TYPE. Eg a one-coordinate pair MULTILINESTRING will
    be returned as a MULTIPOINT.
    :param geos_geom: GEOSGeometry object.
    :return: a GEOSGeometry with valid geometry (geom returns untouched if already valid)
    '''


    '''
    # I like this method instead of executing raw sql, but it requires at least 1 GIS feature in the DB.
    qs = GISFeature.objects.all()[0:1]
    qs = qs.annotate(
        geom_valid=
            Func(
                Func(
                    Value(geos_geom.wkb),
                    function='ST_GeomFromWKB',
                    output_field=GeometryField()
                ),
                function='ST_MakeValid',
                output_field=GeometryField()
            )
    ).values('geom_valid')
    return qs[0]['geom_valid']
    '''

    with connection.cursor() as cursor:
        cursor.execute("SELECT ST_MakeValid(ST_GeomFromWKB(%s));", [geos_geom.wkb,])
        row = cursor.fetchone()
    return GEOSGeometry(row[0], srid=geos_geom.srid)
