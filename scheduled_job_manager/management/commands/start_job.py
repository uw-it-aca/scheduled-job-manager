from django.core.management.base import BaseCommand
from scheduled_job_manager.manager import start_job
from datetime import datetime
import logging


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Start remote job immediately (without regard for scheduling)"

    def add_arguments(self, parser):
        parser.add_argument(
            '--cluster-label', dest='cluster_label', required=True,
            help='Cluster label')
        parser.add_argument(
            '--host-label', dest='host_label', required=True,
            help='Host label')
        parser.add_argument(
            '--job-label', dest='job_label', required=True,
            help='job label')

    def handle(self, *args, **options):
        now = datetime.now()
        cluster = options.get('cluster_label')
        host = options.get('host_label')
        job = options.get('job_label')
        start_job(cluster, host, job)
        logger.info('At {0} signal sent for {1}:{2}:{3}'.format(
            now.strftime('%Y%m%d-%H:%M:%S'), cluster, host, job))
