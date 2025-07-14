import logging

logging.basicConfig(level=logging.DEBUG, format='[%(levelname)s] %(message)s')

def get_logger(name: str) -> logging.Logger:
    """Return a logger with the given name."""
    return logging.getLogger(name)
