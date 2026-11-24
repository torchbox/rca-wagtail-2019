import logging


class OneLineException(logging.Filter):
    """Log an exception as one line, its type and message, without the traceback.

    For loggers that report the same expected failure many times a second, such
    as django-redis when Redis refuses connections, where a full traceback for
    each one floods the logs.
    """

    def filter(self, record):
        if record.exc_info and record.exc_info[1] is not None:
            exc = record.exc_info[1]
            detail = f"{type(exc).__name__}: {exc}".replace("\n", " ")
            record.msg = f"{record.getMessage()}: {detail}"
            record.args = None
            record.exc_info = None
            record.exc_text = None
        return True
