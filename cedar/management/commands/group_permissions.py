import logging
import json
import os
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

from django.conf import settings


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


class Command(BaseCommand):
    help = 'Manage permission groups.'

    def __init__(self, stdout=None, stderr=None, no_color=False):
        super(Command, self).__init__(stdout, stderr, no_color)

    def add_arguments(self, parser):

        parser.add_argument('--dump', action='store_true', dest='dump', default=False,
                            help='Dumps Group Permission assignments to file.')
        parser.add_argument('--load', action='store_true', dest='load', default=False,
                            help='Loads Group Permission assignments from file.')

    def handle(self, *args, **options):
        '''
        :param args:
        :param options:
        :return:
        '''

        if options['dump']:
            self.dump()
        elif options['load']:
            self.load()
            return

    def dump(self):
        self.stdout.write("About to load permission groups.")
        groups = {}
        for g in Group.objects.all():
            groups[g.name] = []
            for p in g.permissions.all():
                groups[g.name].append({
                    'app_label': p.content_type.app_label,
                    'model': p.content_type.model,
                    'codename': p.codename
                })
                self.stdout.write("Writing:{} - {} {} - {}".format(g.name, p.content_type.app_label, p.content_type.model, p.codename))

        with open(os.path.join(settings.DJANGO_ROOT,
                               'cedar', 'fixtures', 'group_permissions.json'), 'w') as out:
            out.write(json.dumps(groups))

    def load(self):
        # to get perm with only need content type (app label + model)  perm.codename
        groups = None
        with open(os.path.join(settings.DJANGO_ROOT,
                               'cedar', 'fixtures', 'group_permissions.json'), 'r') as out:
            groups = json.loads(out.read())

        for g in groups.keys():
            group, created = Group.objects.get_or_create(name=g)
            perms = groups[g]

            for perm in perms:
                try:
                    permission = Permission.objects.get_by_natural_key(perm['codename'], perm['app_label'], perm['model'])
                except Permission.DoesNotExist as e:
                    self.stdout.write("Error! Permission {}:{}:{} could not be found. Exception: {}".
                                      format(perm['codename'], perm['app_label'], perm['model'], str(e)))
                group.permissions.add(permission)
                self.stdout.write("Added {} for group {}".format(permission, group))