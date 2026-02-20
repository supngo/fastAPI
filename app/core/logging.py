import logging
from pythonjsonlogger import jsonlogger

DEFAULT_LOG_LEVEL = logging.INFO


class RequestIdFilter(logging.Filter):
    """
    Ensures every log record has a request_id field,
    so JSON formatter never fails if it's missing.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        if not hasattr(record, "request_id"):
            record.request_id = None
        return True


def setup_logging(level: int = DEFAULT_LOG_LEVEL):
    """
    Configure root logger to output JSON logs suitable for production.
    Works with FastAPI + Gunicorn + Docker stdout collection.
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Remove default handlers (important in uvicorn/gunicorn environments)
    root_logger.handlers.clear()

    handler = logging.StreamHandler()

    formatter = jsonlogger.JsonFormatter(
        fmt="%(asctime)s %(levelname)s %(name)s %(message)s %(request_id)s",
        rename_fields={
            "asctime": "timestamp",
            "levelname": "level",
            "name": "logger",
        },
    )

    handler.setFormatter(formatter)
    handler.addFilter(RequestIdFilter())

    root_logger.addHandler(handler)


def get_logger(name: str = "backend") -> logging.Logger:
    """Return a structured JSON logger."""
    return logging.getLogger(name)
