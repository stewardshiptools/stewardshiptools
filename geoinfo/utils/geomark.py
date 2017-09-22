import requests


class Geomark:
    base_url = "http://apps.gov.bc.ca/pub/geomark/geomarks/"
    base_url_ssl = "https://apps.gov.bc.ca/pub/geomark/geomarks/"

    urls = {
        "GET": {
            "base": "{geomarkId}",  # The url of the Geomark front facing page.  Not an actual API URL.
            "bbox": "{geomarkId}/boundingBox.{fileFormatExtension}",
            "feature": "{geomarkId}/feature.{fileFormatExtension}",
            "info": "{geomarkId}.{fileFormatExtension}",
            "parts": "{geomarkId}/parts.{fileFormatExtension}",
            "point": "{geomarkId}/point.{fileFormatExtension}"
        },
        "POST": {
            "create": "new",
            "copy": "copy"
        }
    }

    formats = {
        'json': 'application/json',
        'xml': 'text/xml',
        'kml': 'application/vnd.google-earth.kml+xml',
        'kmz': 'application/vnd.google-earth.kmz',
        'shp': 'text/html',
        'shpz': 'application/x-shp+zip',
        'geojson': 'application/json',
        'gml': 'application/gml+xml',
        'wkt': 'text/x-wkt'
    }

    def __init__(self, geomark_id=None, srid=4326, **kwargs):
        if geomark_id.startswith(self.base_url) or geomark_id.startswith(self.base_url_ssl):
            geomark_id = geomark_id.replace(self.base_url, '')
            geomark_id = geomark_id.replace(self.base_url_ssl, '')

        self.geomark_id = geomark_id
        self.srid = srid
        self.responses = dict()

        for key, value in kwargs.items():
            setattr(self, key, value)

    @staticmethod
    def available_formats():
        print(', '.join(Geomark.formats.keys()))

    @staticmethod
    def available_get_query_types():
        print(', '.join(Geomark.urls['GET'].keys()))

    @staticmethod
    def available_post_query_types():
        print(', '.join(Geomark.urls['POST'].keys()))

    def get_url(self, query_type="info", geomark_format="geojson"):
        return "%s%s" % (
            self.base_url_ssl,
            self.urls['GET'][query_type].format(geomarkId=self.geomark_id, fileFormatExtension=geomark_format)
        )

    def _prepare_geomark(self, geomark_id=None, geom=None):
        """Prepare a geomark object for any request that requires an existing geomark.

        :param geomark_id: the geomark_id value optionally passed to methods that READ
        """

        # First check if geomark_id exists.  If it does then we're fine
        if self.geomark_id is None:
            # If there's no geomark_id... try the one passed to the method.
            if geomark_id is not None:
                self.geomark_id = geomark_id
            elif geom is not None:
                return Geomark.create(geom)

        return True

    def _prepare_get_request(self, query_type="info", geomark_format='geojson'):
        url = self.get_url(query_type=query_type, geomark_format=geomark_format)

        response = requests.get(url, headers={'Accept': self.formats[geomark_format]}, params={'srid': self.srid})

        if response.status_code == 200:
            self.responses[query_type] = response
            return response.status_code

        # Else... something has gone wrong!  Check the error code!
        if response.status_code == 400:
            raise Exception("400 error returned from the given url.  Unrecognised SRID, %d, was given.  URL: %s" %
                            (self.srid, url))
        elif response.status_code == 404:
            raise Exception("404 error returned from the given url.  No Geomark was found with the given Geomark ID, %s.  URL: %s" %
                            (self.geomark_id, url))
        elif response.status_code == 500:
            raise Exception(
                "500 error returned from the given url.  Internal Server Error.  URL: %s" % url)

        # If no exceptions are raised at this point... something unknown has happened return the response and
        # hope for the best!
        self.responses[query_type] = response
        return response.status_code

    @staticmethod
    def create(geom, multiple=False, buffer_metres=None, buffer_join='ROUND', buffer_cap='ROUND',
               buffer_metre_limit=5, buffer_segments=8):
        """Create a geomark from a provided geometry and set self.geomark_id to its Geomark ID.
        see http://apps.gov.bc.ca/pub/api-explorer/?url=https://raw.githubusercontent.com/bcgov/api-specs/master/geomark/geomark.json#!/create/post_geomarks_new
        for more information.

        :param geom: A geos geometry object
        :return: the geomark_id of the created geomark, or False for failure.
        """
        url = "%s%s" % (
            Geomark.base_url_ssl,
            Geomark.urls['POST']['create']
        )

        post_data = {
            'format': 'geojson',
            'srid': geom.srid or 4326,
            'resultFormat': 'json',
            'multiple': multiple,
            'bufferMetres': buffer_metres,
            'bufferJoin': buffer_join,
            'bufferCap': buffer_cap,
            'bufferMetreLimit': buffer_metre_limit,
            'bufferSegments': buffer_segments,
            'body': geom.geojson
        }

        response = requests.post(url, data=post_data)
        response_json = response.json()
        return Geomark(response_json['id'])

    @staticmethod
    def copy(geomark_objects, buffer_metres=None, buffer_join='ROUND', buffer_cap='ROUND',
               buffer_metre_limit=5, buffer_segments=8):
        """Takes a list of Geomark objects and returns a new one created with the copy function.

        :param geomark_objects: List of Geomark objects
        :return: resulting Geomark object
        """
        # TODO This method is broken... fix it!
        url = "%s%s" % (
            Geomark.base_url_ssl,
            Geomark.urls['POST']['copy']
        )

        geomark_urls = [x.get_url("base") for x in geomark_objects]

        post_data = {
            'geomarkUrl': geomark_urls,
            'resultFormat': 'json',
            'bufferMetres': buffer_metres,
            'bufferJoin': buffer_join,
            'bufferCap': buffer_cap,
            'bufferMetreLimit': buffer_metre_limit,
            'bufferSegments': buffer_segments
        }

        response = requests.post(url, json=post_data)
        response_json = response.json()
        return Geomark(response_json['id'])

    def _load_response(self, query_type="info", geomark_format='geojson', geomark_id=None):
        if not self._prepare_geomark(geomark_id=geomark_id):
            return False

        self._prepare_get_request(query_type, geomark_format)

    def _check_response(self, query_type="info", geomark_format='geojson', geomark_id=None):
        try:
            self.responses[query_type]
        except KeyError:
            self._load_response(query_type, geomark_format=geomark_format, geomark_id=geomark_id)

    def get_response(self, query_type="info", geomark_format='geojson', geomark_id=None):
        self._check_response(query_type, geomark_format=geomark_format, geomark_id=geomark_id)
        return self.responses[query_type]
