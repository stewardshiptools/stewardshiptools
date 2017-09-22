import logging

from django.core.management.base import BaseCommand

from communication.models import Mailbox
from communication.utils import comm_utils

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class Command(BaseCommand):
    def handle(self, *args, **options):
        mailboxes = Mailbox.objects.filter(active=True)
        comm_utils.harvest_mailboxes(mailboxes)
