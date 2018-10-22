from django.urls import path
from scheduled_job_manager.views.manager import JobManager
from scheduled_job_manager.views.api.jobs import JobManagerAPI


urlpatterns = [
    path('', JobManager.as_view()),
    path('api/v1/jobs/', JobManagerAPI.as_view())
]
