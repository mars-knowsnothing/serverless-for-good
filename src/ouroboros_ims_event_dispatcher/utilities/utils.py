import json
import logging
import os
import time
from datetime import datetime
from utilities import logger


class Utils(object):
    def __init__(self, **kwargs):
        # self.AWS = AWS(**kwargs)
        self.logger = logger

    def get_ts(self):
        ts = time.time()
        st = datetime.fromtimestamp(ts).strftime('%Y%m%d%H%M%S')
        return st