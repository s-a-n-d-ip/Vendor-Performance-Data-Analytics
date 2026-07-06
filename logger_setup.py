# logger_setup.py

import logging
from pathlib import Path


def get_logger(log_name, level=logging.INFO):
    """
    Creates and returns a logger with a dedicated log file.

    Parameters:
    ----------
    log_name : str
        Name of the logger and log file.

    level : logging level
        Default = logging.INFO

    Returns:
    -------
    logging.Logger
        Configured logger object.
    """

    # Create logs directory if it does not exist
    LOG_DIR = Path("logs")
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    # Log file path
    LOG_FILE = LOG_DIR / f"{log_name}.log"

    # Create logger
    logger = logging.getLogger(log_name)
    logger.setLevel(level)

    # Prevent duplicate handlers
    if not logger.handlers:

        # File handler
        file_handler = logging.FileHandler(
            filename=LOG_FILE,
            mode='a',
            encoding='utf-8'
        )

        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )

        file_handler.setFormatter(formatter)

        # Add handler to logger
        logger.addHandler(file_handler)

    return logger


# Test execution
if __name__ == "__main__":

    logger = get_logger("test")

    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")
    logger.critical("Critical message")

    print("Logger created successfully.")