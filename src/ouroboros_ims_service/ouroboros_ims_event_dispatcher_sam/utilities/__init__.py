import logging
import os
import time
from functools import wraps

# Define logger
# import boto3

logLevel = os.getenv("logLevel", "INFO")
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
chformatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(chformatter)
logger = logging.getLogger()
logger.setLevel(getattr(logging, logLevel))
logger.addHandler(ch)

# Define DynamoDB resource
# dynamodb = boto3.resource('dynamodb')


def details(func: classmethod):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        logger.debug("{name} start".format(name=func.__name__))
        result = func(*args, **kwargs)
        end = time.time()
        logger.debug("{name} end".format(name=func.__name__))
        logger.debug("{name} duration: {duration} ms".format(name=func.__name__,
                                                             duration=str((end - start) * 1000)))
        return result

    return wrapper