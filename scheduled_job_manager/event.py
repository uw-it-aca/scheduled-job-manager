"""
Process Job Response Queue
"""

from scheduled_job_manager.models import Cluster, Member, Task, Schedule, Job
from scheduled_job_manager.exceptions import (
    UnrecognizedJobResponse, InvalidJobResponse)
from aws_message.processor import InnerMessageProcessor, ProcessorException
from datetime import datetime
from dateutil.parser import parse
import logging


logger = logging.getLogger(__name__)
QUEUE_SETTINGS_NAME = 'JOB_RESPONSE_V1'


class JobResponseProcessorException(ProcessorException):
    pass


class JobResponseProcessor(InnerMessageProcessor):

    EXCEPTION_CLASS = JobResponseProcessorException

    def __init__(self):
        super(JobResponseProcessor, self).__init__(
            logger, queue_settings_name=QUEUE_SETTINGS_NAME)

    def process_inner_message(self, json_data):
        """
        Each status change message body contains a single event
        """
        try:
            cluster, created = Cluster.objects.get_or_create(
                label=json_data['Cluster']['ClusterName'])
            member, created = Member.objects.get_or_create(
                cluster=cluster,
                label=json_data['Cluster']['ClusterMemberName'])
            member.datetime_last_updated = datetime.now()
            member.save()

            action = json_data['Action'].lower()
            data = json_data['Data']

            logger.debug("{0}: {1}".format(action, data))
            if action == 'register':
                # cluster member's available jobs
                for job in data['JobList']:
                    task, create = Task.objects.get_or_create(
                        member=member, label=job)

            elif action == 'launch':
                # specific job start data
                try:
                    label = data['JobLabel']
                    task = Task.objects.get(member=member, label=label)
                    schedule, create = Schedule.objects.get_or_create(
                        task=task)
                    job, create = Job.objects.get_or_create(
                        schedule=schedule, job_id=data['JobId'],
                        datetime_start=parse(data['StartDate']),
                        datetime_last_updated=datetime.now())

                    if job.is_running():
                        logger.error('launch task already running {0}'.format(
                            task.json_data()))

                except Task.DoesNotExist:
                    logger.error('unknown launch task {0}'.format(label))

            elif action == 'exit':
                # specific job exit status and any associated data
                try:
                    job = Job.objects.get(job_id=data['JobId'])
                    job.exit_status = data['ExitStatus']
                    job.exit_output = data['ExitOutput']
                    job.datetime_exit = parse(data['EndDate'])
                    job.save()
                except Job.DoesNotExist:
                    logger.error('unknown exit job {0}'.format(label))

            elif action == 'progress':
                # specific job progress
                logger.debug('progress from {0}'.format(task.json_data()))
                try:
                    job = Job.objects.get(job_id=data['JobId'])
                    job.progress = int(data['Progress'])
                    job.save()
                except Job.DoesNotExist:
                    logger.error('unknown progress job {0}'.format(label))

            elif action == 'ping':
                # response to general health query, datetime recorded above
                logger.debug('ping from {0}'.format(task.json_data()))

            else:
                logger.error('Unrecognized Job Action: {0}'.format(action))
                raise UnrecognizedJobResponse(action)

        except Exception as ex:
            logger.exception('Invalid Job Action: {0}'.format(ex))
            raise InvalidJobResponse('{0}'.format(json_data))
