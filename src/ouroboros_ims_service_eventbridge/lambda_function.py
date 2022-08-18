import json
import botocore
from utilities.aws import AWSUtils

def delete_rule(utils,record):
    response = dict()
    return response

def put_rule(utils,record):
    event_bridge_rule = dict()
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
    event_bridge_rule["resp_put_rule"]=resp_put_rule
    event_bridge_rule["resp_put_targets"]=resp_put_targets

    return event_bridge_rule

def lambda_handler(event, context):
    # TODO implement
    print(event)
    records = event["Records"]
    result = list()
    for record in records:
        utils = AWSUtils(region_name="ap-southeast-1",role_arn="arn:aws:iam::592336536196:role/ouroboros_ims_master")
        try:
            resp_put_rule = put_rule(utils,record)
            utils.logger.info(resp_put_rule)
        except botocore.exceptions.ClientError as error:
            resp_put_rule = error.response["Error"]
            utils.logger.info(resp_put_rule)
        result.append(resp_put_rule)
    return {
        'statusCode': 200,
        'body': json.dumps(result)
    }
