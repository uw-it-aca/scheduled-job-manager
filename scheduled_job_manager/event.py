"""
Process Job Response Queue
"""

from scheduled_job_manager.models import Cluster, Member, Task, Job
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
            if json_data['Type'] != 'ScheduledJobMessage':
                raise InvalidJobResponse(
                    'Unrecognized message type {}'.format(
                        json_data['Type']))

            cluster, created = Cluster.objects.get_or_create(
                label=json_data['Cluster']['ClusterName'])
            member, created = Member.objects.get_or_create(
                cluster=cluster,
                label=json_data['Cluster']['ClusterMemberName'])
            member.datetime_last_updated = datetime.now()
            member.save()

            action = json_data['Action'].lower()
            data = json_data['Data']

            logger.info("{} - {}.{}: {}".format(
                action, cluster.label, member.label, data))
            if action == 'register':
                job_list = data['job_list']

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
                    label = data['job_label']
                    job = Job.objects.get(job_id=data['job_id'])
                    job.datetime_launch = parse(data['start_date'])
                    job.save()

                    if job.is_running():
                        logger.error('launch task already running {0}'.format(
                            job.schedule.task.json_data()))

                except Job.DoesNotExist:
                    logger.error('unknown launch task {0}'.format(label))

            elif action == 'status':
                for job_id, job_state in data['jobs'].items():
                    try:
                        job = Job.objects.get(job_id=job_id)
                        job.progress = int(job_state['progress']) if (
                            job_state['progress']) else None
                        job.exit_status = int(job_state['exit_status']) if (
                            job_state['exit_status']) else None
                        job.exit_output = job_state['exit_output']
                        job.datetime_launch = parse(
                            job_state['start_date']) if (
                                job_state['start_date']) else None
                        job.datetime_start = parse(
                            job_state['start_date']) if (
                                job_state['start_date']) else None
                        job.datetime_exit = parse(job_state['end_date']) if (
                            job_state['end_date']) else None
                        job.save()
                    except Job.DoesNotExist:
                        logger.error('unknown progress job {0}'.format(job_id))

            elif action == 'error':
                # error report
                try:
                    error_cause = data['cause']
                    error_data = data['data']
                    job = Job.objects.get(job_id=data['job_id'])
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

        except (KeyError, UnrecognizedJobResponse, InvalidJobResponse) as ex:
            # log the error, but accept the message as processed
            logger.error('Job Response Error: {}'.format(ex))
        except Exception as ex:
            logger.exception('Job Event Exception: {0}'.format(ex))
            raise JobResponseProcessorException('{0}'.format(json_data))
