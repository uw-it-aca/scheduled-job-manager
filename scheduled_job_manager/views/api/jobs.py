from logging import getLogger
from django.conf import settings
from django.utils.decorators import method_decorator
from scheduled_job_manager.models import Job
from scheduled_job_manager.views.rest_dispatch import RESTDispatch
from uw_saml.decorators import group_required


logger = getLogger(__name__)


def can_manage_jobs():
    return False


@method_decorator(group_required(settings.SCHEDULED_JOB_ADMIN_GROUP),
                  name='dispatch')
class JobManagerAPI(RESTDispatch):
    """ Retrieves a list of Jobs.
    """
    def get(self, request, *args, **kwargs):
        jobs = []
        for job in Job.objects.all():# .order_by(''):
            data = job.json_data()
            jobs.append(data)

        return self.json_response({'jobs': jobs})
