import logging

def setup_logging():
    """Sets up a logger that prints to a file.txt"""
    return logging.getLogger("Chronicle_Logger")

# global instance
logger = setup_logging()