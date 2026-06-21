"""
Purpose: Provide centralized application logging.
"""

import os
import logging
from logging.handlers import RotatingFileHandler

class LoggerManager:

    LOGGER_NAME = "milestone-03-analytics-copilot"
    LOG_DIRECTORY = "logs"
    LOG_FILE = (
        f"{LOG_DIRECTORY}/application.log"
    )

    @classmethod
    def get_logger(cls):
        os.makedirs(cls.LOG_DIRECTORY, exist_ok=True)
        logger = logging.getLogger(cls.LOGGER_NAME)
        
        if logger.handlers:
            return logger

        logger.setLevel(logging.INFO)

        formatter = logging.Formatter(
            "%(asctime)s | "
            "%(levelname)s | "
            "%(filename)s:%(lineno)d | "
            "%(message)s"
        )

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)

        file_handler = RotatingFileHandler(
            cls.LOG_FILE,
            maxBytes=1024 * 1024,
            backupCount=5
        )

        file_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
        return logger
    
logger = LoggerManager.get_logger()