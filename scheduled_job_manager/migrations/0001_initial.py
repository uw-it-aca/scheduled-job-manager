# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2018-09-27 21:37
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Cluster',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(max_length=128)),
            ],
        ),
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('job_id', models.CharField(max_length=36, unique=True)),
                ('datetime_launch', models.DateTimeField(null=True)),
                ('datetime_recent_response', models.DateTimeField(null=True)),
                ('datetime_start', models.DateTimeField(null=True)),
                ('datetime_exit', models.DateTimeField(null=True)),
                ('progress', models.SmallIntegerField(default=-1)),
                ('exit_status', models.SmallIntegerField(null=True)),
                ('exit_output', models.CharField(max_length=512, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Member',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(max_length=128)),
                ('cluster', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='scheduled_job_manager.Cluster')),
            ],
        ),
        migrations.CreateModel(
            name='Schedule',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(max_length=128)),
                ('datetime_last_updated', models.DateTimeField(null=True)),
                ('member', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='scheduled_job_manager.Member')),
            ],
        ),
        migrations.AddField(
            model_name='schedule',
            name='task',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='scheduled_job_manager.Task'),
        ),
        migrations.AddField(
            model_name='job',
            name='schedule',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='scheduled_job_manager.Schedule'),
        ),
    ]
