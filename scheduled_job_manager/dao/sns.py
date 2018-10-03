from scheduled_job_manager import get_job_config
from scheduled_job_manager.exceptions import SNSPublishFailure
import boto3
import json


def notify_job_clients(message_type, message_data):
    """ Send Scheduled Job Clients control notifications
    """
    config = get_job_config()
    client = boto3.client('sns',
                          aws_access_key_id=config.get('KEY_ID'),
                          aws_secret_access_key=config.get('KEY'))
    response = client.publish(
        TopicArn=config.get('NOTIFICATION').get('TOPIC_ARN'),
        Message=json.dumps({
            'Action': message_type,
            'Data': message_data
        }))

    if 'MessageId' not in response:
        raise SNSPublishFailure('bogus publish response: {0}'.format(response))
