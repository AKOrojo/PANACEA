import logging

# Configure logging at the root level of the application
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filename='application.log',
                    filemode='a')

def get_logger(name):
    """
    Returns a logger with the specified name. This function ensures that
    all loggers created through this function share the same configuration.

    :param name: Name of the logger.
    :return: Configured Logger object.
    """
    return logging.getLogger(name)
