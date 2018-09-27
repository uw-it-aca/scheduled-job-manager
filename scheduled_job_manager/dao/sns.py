from scheduled_job_manager import get_job_config
from scheduled_job_manager.exceptions import SNSPublishFailure
import boto3
import json


def notify_job_clients(message_type, message_data):
    """ Send Scheduled Job Clients control notifications
    """
    config = get_job_config()
    message = json.dumps({
        # TODO: sign message with service-manager key?
        # 'signature': sign(self.json_data()),
        'type': message_type,
        'data': message_data
    })

    client = boto3.client('sns',
                          aws_access_key_id=config.KEY_ID,
                          aws_secret_access_key=config.KEY)
    response = client.publish(
        TopicArn=config['NOTIFICATION']['TOPIC_ARN'],
        Message=message,
        MessageStructure='json')

    if 'MessageId' not in response:
        raise SNSPublishFailure('bogus publish response: {0}'.format(response))
