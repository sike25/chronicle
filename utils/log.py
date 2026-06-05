import contextvars
import logging


# Holds the current job_id for the running context (thread/coroutine).
# Set once per job via set_job_id(); every log line picks it up automatically.
_job_id_var: contextvars.ContextVar[str] = contextvars.ContextVar("job_id", default="-")

def set_job_id(job_id: str):
    """Bind a job_id to the current context so all subsequent logs carry it."""
    _job_id_var.set(job_id)


class JobIdFilter(logging.Filter):
    """Injects the context's job_id onto every record as record.job_id."""
    def filter(self, record):
        record.job_id = _job_id_var.get()
        return True


def setup_logging():
    logger = logging.getLogger("Chronicle_Logger")

    if not logger.handlers:
        logger.setLevel(logging.DEBUG)

        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(name)s | job=%(job_id)s | %(message)s'
        )

        # stdout handler (required for Cloud Run)
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        stream_handler.addFilter(JobIdFilter())
        logger.addHandler(stream_handler)

    return logger

# global instance
logger = setup_logging()