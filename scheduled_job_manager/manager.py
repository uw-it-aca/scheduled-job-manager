# job manager control method
from scheduled_job_manager.models import Cluster, Member, Task, Schedule, Job
from scheduled_job_manager.exceptions import (
    ScheduledJobRunning, JobStartFailureException)
from scheduled_job_manager.dao.sns import notify_job_clients
from scheduled_job_manager.event import JobResponseProcessor
from aws_message.gather import Gather
import logging


logger = logging.getLogger(__name__)


def start_job(cluster_label, member_label, task_label):
    """Send SNS notifcation to start job on member in cluster
    """
    try:
        # cluster, member and task need to be "registered" (exist)
        cluster = Cluster.objects.get(label=cluster_label)
        member = Member.objects.get(cluster=cluster, label=member_label)
        task = Task.objects.get(member=member, label=task_label)
        schedule = Schedule.objects.update_or_create(task=task)
        try:
            job, created = Job.objects.get_or_create(schedule=schedule)
            job.launch()
        except ScheduledJobRunning as ex:
            logger.error(
                    'Job {0}:{1}:{2} already running'.format(
                        cluster.label, member.label, task_label))
    except (Cluster.DoesNotExist,
            Member.DoesNotExist, Task.DoesNotExist) as ex:
        raise JobStartFailureException(
            'Cannot start job {0}:{1}:{2} - {3}'.format(
                cluster_label, member_label, task_label, ex))


def query_status():
    """SNS message to query job progress
    """
    notify_job_clients('status', {})


def monitor_job_responses():
    """Peel messages off SQS monitor queue and update cluster/instance data
    """
    try:
        Gather(processor=JobResponseProcessor()).gather_events()
    except Exception as ex:
        logger.exception("Gather JobResponseProcessor: %s" % ex)
