from django.core.management.base import BaseCommand
from scheduled_job_manager.manager import query_member_status
import logging


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Prod cluster members to report status"

    def handle(self, *args, **options):
        try:
            query_member_status()
        except Exception as ex:
            logger.exception('query_status: {0}'.format(ex))
