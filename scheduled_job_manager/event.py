"""
Process Job Response Queue
"""

import logging
from django.utils import timezone
from dateutil.parser import parse
from aws_message.processor import InnerMessageProcessor, ProcessorException


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
        logger.info('AWS MESSAGE JSON: {0}'.format(json_data))
