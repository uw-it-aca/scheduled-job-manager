# Scheduled Job Manager exceptions


class InvalidJobConfig(Exception):
    pass


class JobStartFailureException(Exception):
    pass


class UnrecognizedJobResponse(Exception):
    pass


class InvalidJobResponse(Exception):
    pass


class ScheduledJobRunning(Exception):
    pass


class SNSPublishFailure(Exception):
    pass
