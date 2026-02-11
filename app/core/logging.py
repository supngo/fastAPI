import logging

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )


def get_logger(name: str = "backend") -> logging.Logger:
    """Return a named logger"""
    return logging.getLogger(name)