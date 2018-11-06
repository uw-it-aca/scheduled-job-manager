import os
import channel.asgi

os.environ.setdefault('DJANGO_SETTINGS_MODULE',
                      'scheduled_job_manager.project.settings')
channel_layer = channels.asgi.get_channel_layer()
