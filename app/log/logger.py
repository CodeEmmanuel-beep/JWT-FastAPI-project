from logging.handlers import RotatingFileHandler
import logging
import os


def get_loggers(name: str):
    os.makedirs("logs", exist_ok=True)
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        fmt = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        fh = RotatingFileHandler(
            f"logs{name}.log", maxBytes=5 * 1024 * 1024, backupCount=3
        )
        fh.setFormatter(fmt)
        logger.addHandler(fh)
        ch = logging.StreamHandler()
        ch.setFormatter(fmt)
        logger.addHandler(ch)
    return logger
