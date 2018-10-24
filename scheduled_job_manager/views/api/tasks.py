from logging import getLogger
from django.conf import settings
from django.utils.decorators import method_decorator
from scheduled_job_manager.models import Task
from scheduled_job_manager.views.rest_dispatch import RESTDispatch
from uw_saml.decorators import group_required


logger = getLogger(__name__)


@method_decorator(group_required(settings.SCHEDULED_JOB_ADMIN_GROUP),
                  name='dispatch')
class TaskListAPI(RESTDispatch):
    """ Retrieves a list of Tasks (things that can be launched into jobs).
    """
    def get(self, request, *args, **kwargs):
        tasks = []
        for task in Task.objects.all():
            data = task.json_data()
            tasks.append(data)

        return self.json_response({'tasks': tasks})
