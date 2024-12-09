import logging
import os

# Define log directory
LOGS_DIR = os.path.join(os.getcwd(), "logs")
os.makedirs(LOGS_DIR, exist_ok=True)

# Create formatter
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(funcName)s - %(message)s")

# File handler (always enabled)
file_handler = logging.FileHandler(os.path.join(LOGS_DIR, "application.log"))
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

# Stream handler (console logs, disabled by default)
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.ERROR)  # Adjust log level for console logs
stream_handler.setFormatter(formatter)

def get_logger(name: str, enable_console: bool = False):
    """
    Get a logger with the specified name, with file and optional console handlers.

    Args:
        name (str): Name of the logger (usually __name__ of the module).
        enable_console (bool): Enable console logs if True.

    Returns:
        logging.Logger: Configured logger instance.
    """
    logger = logging.getLogger(name)
    if not logger.hasHandlers():
        logger.setLevel(logging.DEBUG)  # Set the logger level
        logger.addHandler(file_handler)
        if enable_console:
            logger.addHandler(stream_handler)
    return logger
