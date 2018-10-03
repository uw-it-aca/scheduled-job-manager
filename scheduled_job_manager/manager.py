# job manager control method
from scheduled_job_manager.models import Cluster, Member, Task, Schedule, Job
from scheduled_job_manager.exceptions import (
    ScheduledJobRunning, JobStartFailureException)
from scheduled_job_manager.notification import notify_member_status
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
        if task.unavailable:
            raise JobStartFailureException(
                'Task not available - {0}:{1}:{2}'.format(
                    cluster_label, member_label, task_label))

        # BUG: flesh out defaults when Schedule comes to pass
        schedule, created = Schedule.objects.update_or_create(task=task)
        try:
            job, created = Job.objects.get_or_create(schedule=schedule)
            job.launch()
            logger.info(
                    'Job launch {0}:{1}:{2} signal sent'.format(
                        cluster.label, member.label, task_label))
        except ScheduledJobRunning as ex:
            logger.error(
                    'Job {0}:{1}:{2} already running'.format(
                        cluster.label, member.label, task_label))
    except (Cluster.DoesNotExist,
            Member.DoesNotExist, Task.DoesNotExist) as ex:
        raise JobStartFailureException(
            'Cannot start job - {0}:{1}:{2} - {3}'.format(
                cluster_label, member_label, task_label, ex))


def query_job_progress():
    """SNS message to query job progress
    """
    pass


def query_member_status():
    """SNS message to query cluster member status
    """
    notify_member_status()
    logger.info('signal sent for status report')


def monitor_job_responses():
    """Peel messages off SQS monitor queue and update cluster/instance data
    """
    try:
        Gather(processor=JobResponseProcessor()).gather_events()
    except Exception as ex:
        logger.exception("Gather JobResponseProcessor: {0}".format(ex))
