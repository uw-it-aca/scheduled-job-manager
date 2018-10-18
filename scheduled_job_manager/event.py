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
                job_list = data['JobList']

                for known in Task.objects.filter(member=member):
                    if known.label in job_list:
                        job_list.remove(known.label)
                        known.unavailable = None
                    else:
                        known.unavailable = True

                    known.save()

                for label in job_list:
                    Task.objects.create(member=member, label=label)

            elif action == 'launch':
                # specific job start data
                try:
                    label = data['JobLabel']

                    job = Job.objects.get(job_id=data['JobId'])
                    job.datetime_launch = parse(data['StartDate'])
                    job.save()

                    if job.is_running():
                        logger.error('launch task already running {0}'.format(
                            job.task.json_data()))

                except Job.DoesNotExist:
                    logger.error('unknown launch task {0}'.format(label))

            elif action == 'status':
                for job_id, job_state in data['Jobs'].items():
                    try:
                        job = Job.objects.get(job_id=job_id)
                        job.progress = int(job_state['Progress'])
                        job.exit_status = job_state['ExitStatus']
                        job.exit_output = job_state['ExitOutput']
                        job.datetime_exit = parse(job_state['EndDate'])
                        job.save()
                    except Job.DoesNotExist:
                        logger.error('unknown progress job {0}'.format(job_id))

            elif action == 'error':
                # error report
                try:
                    error_cause = data['Cause']
                    error_data = data['Data']
                    job = Job.objects.get(job_id=data['JobId'])
                    logger.error(
                        'error from {0}: cause: {1}: Data: {2}'.format(
                            job.json_data(), error_cause, error_data))

                    if (error_cause == 'invalid_job_label' or
                            error_cause == 'invalid_job_configuration'):
                        job.schedule.task.unavailable = True
                        job.schedule.task.save()
                except Job.DoesNotExist:
                    logger.error(
                        'unknown job reporting error {0}'.format(label))

            else:
                logger.error('Unrecognized Job Action: {0}'.format(action))
                raise UnrecognizedJobResponse(action)

        except Exception as ex:
            logger.exception('Invalid Job Action: {0}'.format(ex))
            raise InvalidJobResponse('{0}'.format(json_data))
