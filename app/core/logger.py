import logging
from logging.handlers import RotatingFileHandler
import sys

def get_logger(name: str = "app"):
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    fmt = logging.Formatter("[%(asctime)s] [%(levelname)s] %(name)s: %(message)s")

    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(fmt)
    ch.setLevel(logging.INFO)

    fh = RotatingFileHandler("app.log", maxBytes=2_000_000, backupCount=3)
    fh.setFormatter(fmt)
    fh.setLevel(logging.INFO)

    logger.addHandler(ch)
    logger.addHandler(fh)
    return logger

logger = get_logger()
