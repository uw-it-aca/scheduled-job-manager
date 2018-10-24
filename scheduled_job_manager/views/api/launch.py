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
            job_cluster = Job.objects.get(job_id=kwargs['job_cluster'])
            job_member = Job.objects.get(job_id=kwargs['job_member'])
            job_label = Job.objects.get(job_id=kwargs['job_label'])
            start_job(job_cluster, job_member, job_label)
        except Job.DoesNotExist:
            self.error_response(404, 'Unknown Job ID')

        return self.json_response({'job': job.json_data()})
