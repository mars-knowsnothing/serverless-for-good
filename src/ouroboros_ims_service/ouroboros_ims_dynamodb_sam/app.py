import json
from resources.ec2 import Instance
from resources.schedule import Rule,Log


def lambda_handler(event, context):
    # TODO implement
    if '/resources/schedule/rules' in event["resource"]:
        svc = Rule()
    elif '/resources/schedule/logs' in event["resource"]:
        svc = Log()
    response = svc.API(event=event)
    return response
