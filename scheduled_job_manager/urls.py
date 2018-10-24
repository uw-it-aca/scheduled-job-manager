from django.urls import path, re_path
from scheduled_job_manager.views.manager import JobManager
from scheduled_job_manager.views.api.jobs import JobManagerAPI
from scheduled_job_manager.views.api.launch import JobLaunchAPI
from scheduled_job_manager.views.api.tasks import TaskListAPI


urlpatterns = [
    path('', JobManager.as_view()),
    path('api/v1/jobs/', JobManagerAPI.as_view()),
    path('api/v1/tasks/', TaskListAPI.as_view()),
    re_path(r'api/v1/launch/(?P<job_cluster>[\da-zA-Z\-]+)/'
            r'(?P<job_member>[\da-zA-Z\-]+)/'
            r'(?P<job_label>[\da-zA-Z\-]+)/$',
            JobLaunchAPI.as_view())
]
