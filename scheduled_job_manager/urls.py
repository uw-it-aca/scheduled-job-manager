from django.urls import re_path
from scheduled_job_manager.views.api.jobs import JobManager


urlpatterns = [
    re_path(r'api/v1/jobs$', JobManager.as_view()),
#    url(r'api/v1/monitor$', JobMonitor.as_view()),
]
