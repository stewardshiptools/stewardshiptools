from django.core.management.base import BaseCommand, CommandError
from django.contrib.contenttypes.models import ContentType

from heritage.models import Interview
from heritage.utils.sanitizer import interview_populate_sensitive_phrases
from sanitizer.models import RelatedSensitivePhrase


class Command(BaseCommand):
    help = 'Manage RelatedSensitivePhrase objects for interviews.  By default this command generates new ones, but ' \
           'can be used to delete/replace existing ones as well.'

    def __init__(self, stdout=None, stderr=None, no_color=False):
        super(Command, self).__init__(stdout, stderr, no_color)

        self.interviews = None

    def add_arguments(self, parser):
        parser.add_argument('interview_id', nargs='*', type=int,
                            help='(Optional) A list of interview IDs.  Will process all interviews if not included.')

        # Some optional named tags
        parser.add_argument('--delete', action='store_true', dest='delete', default=False,
                            help='Delete RelatedSensitivePhrase objects instead of creating them.')

        parser.add_argument('--overwrite', action='store_true', dest='overwrite', default=False,
                            help='Delete RelatedSensitivePhrase objects before recreating them.')

    def handle(self, *args, **options):
        if options['interview_id']:
            interviews = Interview.objects.filter(id__in=options['interview_id'])
        else:
            interviews = Interview.objects.all()

        self.interviews = interviews

        if options['delete']:
            self.delete_phrases()
        elif options['overwrite']:
            self.delete_phrases()
            self.generate_phrases()
        else:
            self.generate_phrases()

    def delete_phrases(self):
        num_phrases = 0
        interview_content_type = ContentType.objects.get_for_model(Interview)

        for interview in self.interviews:
            phrases = RelatedSensitivePhrase.objects.filter(
                content_type__pk=interview_content_type.id,
                object_id=interview.id
            )
            num_phrases += phrases.count()
            phrases.delete()

        if num_phrases == 1:
            pluralize_phrase = 'phrase'
        else:
            pluralize_phrase = 'phrases'
        self.stdout.write("Successfully deleted %d %s" % (num_phrases, pluralize_phrase))

    def generate_phrases(self):
        num_phrases = 0

        for interview in self.interviews:
            count = interview_populate_sensitive_phrases(interview)
            num_phrases += count

        if num_phrases == 1:
            pluralize_phrase = 'phrase'
        else:
            pluralize_phrase = 'phrases'
        self.stdout.write("Successfully generated %d %s" % (num_phrases, pluralize_phrase))
