from django.conf.urls import url
from scheduled_job_manager.views.api.jobs import JobManager


urlpatterns = [
    url(r'api/v1/jobs$', JobManager.as_view()),
#    url(r'api/v1/monitor$', JobMonitor.as_view()),
]
