from django.core.management.base import BaseCommand
from scheduled_job_manager.manager import monitor_job_responses
import logging


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Collect messages from job response sqs"

    def handle(self, *args, **options):
        try:
            monitor_job_responses()
        except Exception as ex:
            logger.exception('process_job_responses: {0}'.format(ex))
