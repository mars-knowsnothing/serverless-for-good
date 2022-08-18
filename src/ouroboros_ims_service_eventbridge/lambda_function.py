import json
import botocore
from utilities.aws import AWSUtils

def delete_rule(utils,record):
    result = dict()
    client = utils.client("events")
    payload = json.loads(record["body"])
    resp_remove_targets = client.remove_targets(
        Rule="ouroboros-ims-event-{name}".format(name=payload["name"]).lower(),
        EventBusName=payload.get("eventBusName","default"),
        Force=payload.get("force",False),
        Ids=[
            payload["targetId"],
        ],
    )
    resp_delete_rule = client.delete_rule(
        Name="ouroboros-ims-event-{name}".format(name=payload["name"]).lower(),
        EventBusName=payload.get("eventBusName","default"),
        Force=payload.get("force",False),
    )
    result["resp_remove_targets"]=resp_remove_targets
    result["resp_delete_rule"]=resp_delete_rule

    return result

def put_rule(utils,record):
    result = dict()
    client = utils.client("events")
    payload = json.loads(record["body"])
    utils.logger.info(payload)
    params = dict(
        Name="ouroboros-ims-event-{name}".format(name=payload["name"]).lower(),
        State=payload.get("state","ENABLED"),
        Description=payload.get("description","created by ouroboros ims"),
        EventBusName=payload.get("eventBusName","default"),
        Tags=payload.get("tags",[])
    )
    if payload.get("roleArn"):
        params["RoleArn"] = payload["roleArn"]
    
    if payload.get("scheduleExpression"):
        params["ScheduleExpression"] = payload["scheduleExpression"]
    elif payload.get("eventPattern"):
        params["EventPattern"] = payload["eventPattern"]
    resp_put_rule = client.put_rule(**params)
    utils.logger.info(payload)
    resp_put_targets = client.put_targets(
        Rule=params["Name"],
        EventBusName=params["EventBusName"],
        Targets=[
            {
                'Id': payload["targetId"],
                'Arn': payload["targetArn"],
                # 'SqsParameters': {
                #    'MessageGroupId': payload["messageGroupId"]
                #},
                'Input': json.dumps(payload["input"])
            }
        ]
    )
    print(resp_put_rule)
    print(resp_put_targets)
    result["resp_put_rule"]=resp_put_rule
    result["resp_put_targets"]=resp_put_targets

    return result

def lambda_handler(event, context):
    # TODO implement
    print(event)
    records = event["Records"]
    result = list()
    for record in records:
        utils = AWSUtils(region_name="ap-southeast-1",role_arn="arn:aws:iam::592336536196:role/ouroboros_ims_master")
        if record["attributes"]["MessageGroupId"]=="event_bridge_put_rule":
            try:
                resp_put_rule = put_rule(utils,record)
            except botocore.exceptions.ClientError as error:
                resp_put_rule = error.response["Error"]
            utils.logger.info(resp_put_rule)
            result.append(resp_put_rule)
        elif record["attributes"]["MessageGroupId"]=="event_bridge_delete_rule":
            try:
                resp_delete_rule = delete_rule(utils,record)
            except botocore.exceptions.ClientError as error:
                resp_delete_rule = error.response["Error"]
            utils.logger.info(resp_delete_rule)
            result.append(resp_delete_rule)
    return {
        'statusCode': 200,
        'body': json.dumps(result)
    }
