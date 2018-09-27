# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from scheduled_job_manager.init import init_job_manager
from django.apps import AppConfig


class JobManagerConfig(AppConfig):
    name = 'scheduled_job_manager'

    def ready(self):
        init_job_manager()
