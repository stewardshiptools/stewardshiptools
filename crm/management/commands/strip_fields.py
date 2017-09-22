from django.core.management.base import BaseCommand, CommandError
from django.contrib.contenttypes.models import ContentType
from django.db.models.fields import CharField

from cedar.fields import StrippedCharField

class Command(BaseCommand):
    help = 'Use this this strip strings stored in Char fields in the supplied model. Be careful, this is dangerous.'

    def __init__(self, stdout=None, stderr=None, no_color=False):
        super(Command, self).__init__(stdout, stderr, no_color)

        self.interviews = None

    def add_arguments(self, parser):
        parser.add_argument('contenttype', type=str,
                            help='ContentType of the model you wish to process. Careful, if you have two models'
                                 'with the same name this will cause an error.')

    def handle(self, *args, **options):
        model_class = ContentType.objects.get(model=options['contenttype']).model_class()
        self.stdout.write("Stripping fields for {}".format(options['contenttype']))

        queryset = model_class.objects.all()
        for instance in queryset:
            changes_made = False
            for field in instance._meta.get_fields():
                if field.__class__ is CharField or field.__class__ is StrippedCharField:
                    # for instance.field in queryset.model._meta.get_fields():
                    val = getattr(instance, field.name)
                    if val is not None:
                        new_val = str(val).strip()
                        self.stdout.write(
                            "Stripping field {} for {}. Old Value: \"{}\" New Value: \"{}\"".format(
                                field.name,
                                options['contenttype'],
                                val,
                                new_val
                            ))
                        setattr(instance, field.name, new_val)
                        changes_made = True
                if changes_made:
                    instance.save()
