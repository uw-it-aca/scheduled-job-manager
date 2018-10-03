from scheduled_job_manager.dao.sns import notify_job_clients


def notify_member_status():
    """Prompt cluster members to report status
    """
    notify_job_clients('status', {})


def notify_job_start(json_data):
    """Prompt cluster member to start job
    """
    notify_job_clients('launch', json_data)


def notify_job_progress(json_data):
    """Prompt cluster member for job progress
    """
    notify_job_clients('progress', json_data)
