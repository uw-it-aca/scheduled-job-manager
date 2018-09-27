from django.conf import settings
from scheduled_job_manager.exceptions import InvalidJobConfig


def get_job_config():
    try:
        return settings.SCHEDULED_JOB_MANAGER
    except AttributeError as ex:
        raise InvalidJobConfig('Missing Scheduled Job Manager Configuration')
