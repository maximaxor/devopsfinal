import logging
from logging.handlers import RotatingFileHandler
import os


def setup_logger():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Ensure the logs directory exists
    if not os.path.exists('logs'):
        os.makedirs('logs')

    log_file_path = os.path.join('logs', 'error.log')
    
    if not logger.handlers:
        handler = RotatingFileHandler(log_file_path, maxBytes=1024 * 1024 * 100, backupCount=20)
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger