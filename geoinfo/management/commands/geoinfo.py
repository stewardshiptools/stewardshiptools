from django.core.management.base import BaseCommand, CommandError

from geoinfo.models import GISLayerMaster
from geoinfo.utils.layers import GeomParser


class Command(BaseCommand):
    help = 'Manage geoinfo things.'

    def __init__(self, stdout=None, stderr=None, no_color=False):
        super(Command, self).__init__(stdout, stderr, no_color)

    def add_arguments(self, parser):

        parser.add_argument('--rebuild-layers', action='store_true', dest='rebuild_layers', default=False,
                            help='Call GeomParser.process_geoinfo_to_layer() on every GISLayerMaster in the database')

    def handle(self, *args, **options):
        '''
        :param args:
        :param options:
        :return:
        '''
        layers_qs = None

        if options['rebuild_layers']:
            layers_qs = GISLayerMaster.objects.all()
            self.rebuild_layers(layers_qs)

        else:
            self.stdout.write("A valid option was not given. Exiting.")
            return

    def rebuild_layers(self, layers_qs):
        count = 1
        for layer in layers_qs:
            try:
                gp = GeomParser(layer)
                gp.process_geoinfo_to_layer()
            except Exception as e:
                self.stdout.write("Exception occurred processing layer id: {}, layer title: {} : {}".format(layer.id, layer.name, str(e)))

            self.stdout.write("layers processed:{}".format(count))
            count += 1
