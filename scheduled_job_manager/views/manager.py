from django.conf import settings
from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from userservice.user import UserService
from uw_saml.decorators import group_required
import logging


logger = logging.getLogger(__name__)


@method_decorator(group_required(settings.SCHEDULED_JOB_ADMIN_GROUP),
                  name='dispatch')
class JobManager(TemplateView):
    template_name = 'manager.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["user"] = {
                "netid": UserService().get_user()
        }

        return context
