import json
from resources.ec2 import Instance
from resources.schedule import Rule


def lambda_handler(event, context):
    # TODO implement
    if event["resource"] == "/resources/ec2/instances":
        svc = Instance()
    elif event["resource"] == "/resources/schedule/rules":
        svc = Rule()
    response = svc.API(event=event)
    return response
