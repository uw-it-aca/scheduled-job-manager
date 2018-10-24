from logging import getLogger
from django.conf import settings
from django.utils.decorators import method_decorator
from scheduled_job_manager.models import Job
from scheduled_job_manager.manager import start_job
from scheduled_job_manager.views.rest_dispatch import RESTDispatch
from uw_saml.decorators import group_required


logger = getLogger(__name__)


def can_manage_jobs():
    return False


@method_decorator(group_required(settings.SCHEDULED_JOB_ADMIN_GROUP),
                  name='dispatch')
class JobLaunchAPI(RESTDispatch):
    """ Retrieves a list of Jobs.
    """
    def get(self, request, *args, **kwargs):
        try:
            cluster = kwargs['job_cluster']
            member = kwargs['job_member']
            job_label = kwargs['job_label']
            job = Job.objects.get(
                schedule__task__label=job_label,
                schedule__task__member__label=member,
                schedule__task__member__cluster__label=cluster)

            if job.is_running():
                return self.json_response({'status': 'already running'})

            start_job(cluster, member, job_label)
        except Job.DoesNotExist:
            start_job(cluster, member, job_label)

        return self.json_response({'status': 'ok'})
