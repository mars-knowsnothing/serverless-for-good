import json
from resources.ec2 import Instance
from resources.schedule import Rule


def lambda_handler(event, context):
    # TODO implement
    svc = Rule()
    response = svc.API(event=event)
    return response
