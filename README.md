
# Scheduled-Job-Manager
This is the repository for the scheduled job manager project, a project at the University of Washington designed to provide centralized periodic job management.

ACA Schedule Job Manager App
============================

A Django Application on which to build AWS SNS endpoints and SQS gatherers

Installation
------------

**Project directory**

Install django-aws-message in your project.

    $ cd [project]
    $ pip install -e git+https://github.com/uw-it-aca/scheduled-job-manager/#egg=scheduled_job_manager

Project settings.py
------------------

**Job Manager App Settings**

    # Job Manager Configuration
    SCHEDULED_JOB_MANAGER = {
        'KEY_ID': '<aws_key_id>',
        'KEY': '<aws_key>',
        'RESOLUTION': 15,
        'NOTIFICATION': {
            'PROTOCOL': 'http',
            'TOPIC_ARN': '<aws_arn_for_job_control_sns>',
        },
        'STATUS': {
            'TOPIC_ARN': '<aws_arn_for_job_sqs>',
            'QUEUE_URL': '<url_for_aws_job_sqs>'
        }
    }

    # Response Queue Configureation
    AWS_SQS = {
        'JOB_RESPONSE_V1' : {
            'TOPIC_ARN': 'arn:aws:sqs:...',
            'KEY_ID': '<longrandomlookingstring>',
            'KEY': '<longermorerandomlookingstring>',
            'VISIBILITY_TIMEOUT': 60,
            'MESSAGE_GATHER_SIZE': 10,
            'VALIDATE_SNS_SIGNATURE': False,
            'PAYLOAD_SETTINGS': {
                'VALIDATE_MSG_SIGNATURE': True
            }
        }
    }
