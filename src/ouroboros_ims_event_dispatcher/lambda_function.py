import json
from utilities.aws import AWSUtils

class Dispatcher(object):

    def dispatch(self, streamEvent:dict) -> dict:
        return


def lambda_handler(event, context):
    records = event["Records"]
    result = list()
    for record in records:
        utils = AWSUtils(region_name="ap-southeast-1",role_arn="arn:aws:iam::592336536196:role/ouroboros_ims_master")
    return result
