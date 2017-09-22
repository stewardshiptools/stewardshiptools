import sys
import json
import timeit  # use this fun guy if you don't care about a function return value.
import time

from django.core.urlresolvers import reverse
from django.test import TestCase
from django.core.files import File

from cedar.utils import test_utils
from assets import asset_helpers

from .serializers import GISFeatureGeoJSONSerializer

from .models import GISLayer



class FeatureSerializerTests(TestCase):
    def setUp(self):
        test_utils.create_test_user_and_log_in(self.client)
        print("....................................")
        print("FeatureSerializerTests: setUp begin.")
        f1 = open(r'./geoinfo/test_data/shp/zip.zip', 'rb')
        f2 = open(r'./geoinfo/test_data/shp/PROVINCIAS.zip', 'rb')
        shp1 = File(file=f1)
        shp2 = File(file=f2)

        shp1_time = timeit.timeit(
            lambda shp=shp1: GISLayer(name="TESTSHP1", file=shp, input_type='file').save(),
            number=1)

        shp2_time = timeit.timeit(
            lambda shp=shp2: GISLayer(name="TESTSHP2", file=shp, input_type='file').save(),
            number=1)

        f1.close()
        f2.close()

        print("shp1 loaded. time: ", shp1_time)
        print("shp2 loaded. time: ", shp2_time)

        print("FeatureSerializerTests: setUp end.")
        print("....................................")

    # ------------------------------------------------------------------------
    # test_list doesn't really test anything serious and should be re-written to
    # do something useful.
    def test_list(self):
        print("Begin test_list")

        url = reverse('geoinfo:api:layer-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode())
        self.assertGreaterEqual(len(data), 1)

    # ------------------------------------------------------------------------
    # test_download_big_layer_geojson:
    #   makes a request to drf api to download the features of the larger layer,
    #   records the time taken and the size of the download.
    def test_download_big_layer_geojson(self):
        print("Begin test_download_big_layer_geojson")

        gl = GISLayer.objects.get(name="TESTSHP2")

        url = "{}?{}={}".format(reverse('geoinfo:api:feature-list'), 'layer', gl.id)

        time_elapsed, response = test_utils.function_timer(
            lambda url_str=url: self.client.get(url_str),
            url
        )

        data = json.loads(response.content.decode())
        size_of_json = sys.getsizeof(json.dumps(data))
        print("time to download big layer geojson via url {}: {}".format(url, time_elapsed))
        print("size of geojson download:", asset_helpers.sizeof_fmt(size_of_json))
        # print("result:", data)
        self.assertLessEqual(time_elapsed, 20)
        self.assertGreaterEqual(size_of_json, 33000000)
        self.assertLessEqual(size_of_json, 37000000)
