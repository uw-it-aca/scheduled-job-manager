# Scheduled Job Manager exceptions


class InvalidJobConfig(Exception):
    pass


class ScheduledJobRunning(Exception):
    pass


class SNSPublishFailure(Exception):
    pass
