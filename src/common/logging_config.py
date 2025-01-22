import logging
import os
import watchtower                                   # For AWS CloudWatch logging
from logging.handlers import RotatingFileHandler    # For local file storage logging
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

APP_ENV = os.getenv("APP_ENV", "development")

def setup_logger():
    """
    Set up the logger based on the application environment and reuse it across the application.
    """
    # Create the logger
    logger = logging.getLogger("app_logger")
    logger.setLevel(logging.DEBUG)  # Capture all logs from debug level and higher

    # Remove any existing handlers, if present
    if logger.hasHandlers():
        logger.handlers.clear()

    # Configure handler based on environment
    if APP_ENV == "production":     
        # TODO : implement this section in future 
        # TODO : log timestamp should be in UTC in prod env
        cloudwatch_handler = watchtower.CloudWatchLogHandler(log_group="YourLogGroup", stream_name="YourStreamName")
        logger.addHandler(cloudwatch_handler)

        # Handler for Error logs in production
        error_handler = watchtower.CloudWatchLogHandler(log_group="ErrorLogGroup", stream_name="ErrorStreamName")
        error_handler.setLevel(logging.ERROR)
        logger.addHandler(error_handler)

    else:
        # Create the logs directory if it doesn't exist
        log_dir = "logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # Define log format
        log_formatter = logging.Formatter(
            "%(asctime)s - %(filename)s - %(lineno)d - %(levelname)s - %(message)s"
        )

        # Handler for Info logs
        info_handler = RotatingFileHandler(os.path.join(log_dir, "info.log"), maxBytes=10**6, backupCount=5)
        info_handler.setLevel(logging.INFO)     # Set logging level
        info_handler.addFilter(lambda record: record.levelno == logging.INFO)  # Filter out all logs except INFO
        info_handler.setFormatter(log_formatter)
        logger.addHandler(info_handler)

        # Handler for Error logs
        error_handler = RotatingFileHandler(os.path.join(log_dir, "error.log"), maxBytes=10**6, backupCount=5)
        error_handler.setLevel(logging.ERROR)
        error_handler.addFilter(lambda record: record.levelno == logging.ERROR)
        error_handler.setFormatter(log_formatter)
        logger.addHandler(error_handler)

        # Handler for Debug logs
        debug_handler = RotatingFileHandler(os.path.join(log_dir, "debug.log"), maxBytes=10**6, backupCount=5)
        debug_handler.setLevel(logging.DEBUG)
        debug_handler.addFilter(lambda record: record.levelno == logging.DEBUG) 
        debug_handler.setFormatter(log_formatter)
        logger.addHandler(debug_handler)

    return logger

# Initialize logger for the whole app
logger = setup_logger()