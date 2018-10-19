# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from scheduled_job_manager.notification import notify_job_start
from scheduled_job_manager.exceptions import ScheduledJobRunning
from uuid import uuid1
from django.utils.timezone import localtime
from datetime import datetime, timedelta
from logging import getLogger


logger = getLogger(__name__)


class Cluster(models.Model):
    """Registered job cluster
    """
    label = models.CharField(max_length=128)


class Member(models.Model):
    """Registered job cluster member
    """
    cluster = models.ForeignKey(Cluster,
                                on_delete=models.PROTECT)
    label = models.CharField(max_length=128)
    datetime_last_updated = models.DateTimeField(null=True)


class Task(models.Model):
    """Registered job label for given cluster member
    """
    member = models.ForeignKey(Member,
                               on_delete=models.PROTECT)
    label = models.CharField(max_length=128)
    unavailable = models.NullBooleanField()
    datetime_last_updated = models.DateTimeField(null=True)

    def is_stale(self):
        return self.datetime_last_updated < (
            datetime.now() - timedelta(minutes=10))

    def json_data(self):
        return {
            'cluster': self.member.cluster.label,
            'member': self.member.label,
            'label': self.label
        }


class Schedule(models.Model):
    """Represents a job's schedule
    """
    WEEKDAY_SUNDAY = 'sunday'
    WEEKDAY_MONDAY = 'monday'
    WEEKDAY_TUESDAY = 'tuesday'
    WEEKDAY_WEDNESDAY = 'wednesday'
    WEEKDAY_THURSDAY = 'thursday'
    WEEKDAY_FRIDAY = 'friday'
    WEEKDAY_SATURDAY = 'saturday'

    WEEKDAY_CHOICES = [
        (WEEKDAY_SUNDAY, WEEKDAY_SUNDAY),
        (WEEKDAY_MONDAY, WEEKDAY_MONDAY),
        (WEEKDAY_TUESDAY, WEEKDAY_TUESDAY),
        (WEEKDAY_WEDNESDAY, WEEKDAY_WEDNESDAY),
        (WEEKDAY_THURSDAY, WEEKDAY_THURSDAY),
        (WEEKDAY_FRIDAY, WEEKDAY_FRIDAY),
        (WEEKDAY_SATURDAY, WEEKDAY_SATURDAY)
    ]

    task = models.ForeignKey(Task, on_delete=models.PROTECT)
    # weekday = models.MultipleChoiceFields(choices=WEEKDAY_CHOICES)

    # seconds
    # minutes
    # hours
    # week_days
    # month_days
    # months

    def json_data(self):
        return {
            'task': self.task.json_data(),
            'schedule': None
        }


class JobManager(models.Manager):
    def running(self):
        return super(JobManager, self).get_queryset().filter(
            exit_status__isnull=True)


class Job(models.Model):
    """Represents a scheduled job that is running
    """
    schedule = models.ForeignKey(Schedule, on_delete=models.PROTECT)
    job_id = models.CharField(max_length=36, unique=True)
    datetime_launch = models.DateTimeField(null=True)
    datetime_recent_response = models.DateTimeField(null=True)
    datetime_start = models.DateTimeField(null=True)
    datetime_exit = models.DateTimeField(null=True)
    progress = models.SmallIntegerField(null=True)
    exit_status = models.SmallIntegerField(null=True)
    exit_output = models.CharField(max_length=512, null=True)

    objects = JobManager()

    def save(self, *args, **kwargs):
        if not self.job_id:
            self.job_id = uuid1()

        super(Job, self).save(*args, **kwargs)

    def is_running(self):
        return self.exit_status is None

    def json_data(self):
        return {
            'job_id': '{}'.format(self.job_id),
            'task': self.schedule.task.json_data(),
            'datetime_launch': localtime(
                self.datetime_launch).isoformat() if (
                    self.datetime_launch is not None) else None,
            'datetime_recent_response': localtime(
                self.datetime_recent_response).isoformat() if (
                    self.datetime_recent_response is not None) else None,
            'datetime_start': localtime(
                self.datetime_start).isoformat() if (
                    self.datetime_start is not None) else None,
            'datetime_exit': localtime(
                self.datetime_exit).isoformat() if (
                    self.datetime_exit is not None) else None,
            'progress': self.progress,
            'exit_status': self.exit_status,
            'exit_output': self.exit_output
        }

    def launch(self):
        notify_job_start(self.json_data())
