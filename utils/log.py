import logging
import os
import random
from datetime import datetime

os.makedirs("./logs", exist_ok=True)
LOG_FILE = f"./logs/chronicle_logs_{datetime.now().date()}_{random.randint(1, 500)}.txt"

def setup_logging():
    logger = logging.getLogger("Chronicle_Logger")
    
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)

        # file handler (useful for local dev)
        # file_handler = logging.FileHandler(LOG_FILE, mode='a')
        # file_handler.setFormatter(logging.Formatter(
        #     '%(asctime)s | %(levelname)s | %(name)s | %(message)s'
        # ))
        # logger.addHandler(file_handler)

        # stdout handler (required for Cloud Run)
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(logging.Formatter(
            '%(asctime)s | %(levelname)s | %(name)s | %(message)s'
        ))
        logger.addHandler(stream_handler)

    return logger

# global instance
logger = setup_logging()