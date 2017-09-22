import os
from django.core.management.base import BaseCommand, CommandError

from help.models import HelpText, PageHelp

import help

help_path = os.path.dirname(help.__file__)
h_text_template_dir = os.path.join(help_path, "templates/help_texts")

files_to_skip = ["__init__.py", ]

class Command(BaseCommand):
    help = 'Manage help texts.'

    def __init__(self, stdout=None, stderr=None, no_color=False):
        super(Command, self).__init__(stdout, stderr, no_color)

    def add_arguments(self, parser):

        # Some optional named tags
        parser.add_argument('--dump', action='store_true', dest='dump', default=False,
                            help='Dumps all help texts to the help text template folder.')

        parser.add_argument('--ingest', action='store_true', dest='ingest', default=False,
                            help='Pulls all help texts from the help text template folder into HelpText records.')

        parser.add_argument('--purge', action='store_true', dest='purge', default=False,
                            help='Purges all Help records. Helpful for loadding Help fixtures with loaddata afterwards.')

    def handle(self, *args, **options):
        if options['dump']:
            self.dump()
        elif options['ingest']:
            self.ingest()
        elif options['purge']:
            self.purge()
        else:
            self.stdout.write("'dump' or 'ingest' are required arguments.")

    def dump(self):
        if not os.path.exists(h_text_template_dir):
            os.makedirs(h_text_template_dir)

        for h in HelpText.objects.all():
            path = os.path.join(help_path, h_text_template_dir, h.title.replace(":", "__") + ".html")
            print("Dumping {} to {}".format(h.title, path))
            with open(path, 'w') as f:
                f.write(h.html)
        self.stdout.write("Successfully dumped {} HelpText instances".format(HelpText.objects.count()))

    def ingest(self):
        created_count = 0
        for root, dirs, files in os.walk(os.path.join(help_path, h_text_template_dir)):
            for fname in files:
                if fname in files_to_skip:
                    continue
                help_text_title, ext = os.path.splitext(fname)
                h, created = HelpText.objects.get_or_create(title=help_text_title)
                with open(os.path.join(root, fname), 'r') as helpfile:
                    h.html = helpfile.read()
                h.save()

                if created:
                    created_count += 1
                    self.stdout.write("created {} for {}".format(h.title, fname))
            break
        self.stdout.write("Successfully ingested {} help files. Created {} new instances".format(len(files), created_count))

    def purge(self):
        PageHelp.objects.all().delete()
        HelpText.objects.all().delete()
