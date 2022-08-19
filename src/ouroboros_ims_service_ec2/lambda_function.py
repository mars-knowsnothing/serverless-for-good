import json
import botocore
import boto3
from utilities.aws import AWSUtils
from utilities.complex_encoder import ComplexEncoder
from datetime import datetime, timezone, timedelta

TIME_ZONE = timezone(timedelta(hours=8))
dynamodb = boto3.resource('dynamodb')
log_table = dynamodb.Table('cmdb_dev_schedule_logs')

def event_log(event):
    now = datetime.utcnow().astimezone(TIME_ZONE)
    updated_at = now.strftime("%Y-%m-%d %H:%M:%S")
    _ = event.copy()
    _["updatedAt"] = updated_at
    _ = json.loads(json.dumps(_,cls=ComplexEncoder))
    response = log_table.put_item(
        Item=_,
    )
    return response

def get_filters(filters: dict = {}) -> dict:
    _available_filters = ["vpc-id", "instance-id","tag","private-ip-address"]
    _filters = list()
    for k, v in filters.items():
        if k not in _available_filters and k.split(":")[0] not in _available_filters:
            continue
        _filters.append({
            'Name': k,
            'Values': v.split(',')
        })
    return _filters

def describe_instances(utils, MaxResults=50, DryRun=False, filters={}):
    client = utils.client("ec2")
    params = dict(
        MaxResults=MaxResults,
        DryRun=DryRun
    )
    if filters:
        params["Filters"]=get_filters(filters)
    utils.logger.info(params)
    ec2_instances = list()
    response = client.describe_instances(**params)
    for Reservation in response["Reservations"]:
        ec2_instances.extend(Reservation["Instances"])
    while "NextToken" in response:
        response = client.describe_instances(
            NextToken=response["NextToken"],
            **params
        )
        ec2_instances.extend(Reservation["Instances"])
    return ec2_instances

def start_instances(utils,InstanceIds,DryRun=False):
    client = utils.client("ec2")
    response = client.start_instances(
            InstanceIds=InstanceIds,
            # AdditionalInfo='string',
            DryRun=DryRun
        )
    return response

def stop_instances(utils,InstanceIds, Hibernate=False, Force=False, DryRun=False):
    client = utils.client("ec2")
    response = client.stop_instances(
        InstanceIds=InstanceIds,
        Hibernate=Hibernate,
        DryRun=DryRun,
        Force=Force
    )
    return response

def lambda_handler(event, context):
    # TODO implement
    print(event)
    records = event["Records"]
    result = list()
    for record in records:
        print(record)
        params = json.loads(record["body"])
        accountId = params["accountId"]
        utils = AWSUtils(region_name="ap-southeast-1",role_arn="arn:aws:iam::{accountId}:role/ouroboros_ims_master".format(accountId=accountId))
        try:
            instances = describe_instances(utils,filters=params["filters"])
            if params["action"]=="start_instances":
                resp = start_instances(utils,[i["InstanceId"] for i in instances])

            elif params["action"]=="stop_instances":
                resp = stop_instances(utils,[i["InstanceId"] for i in instances])
            event_log(dict(
                eventId=record["messageId"],
                targets=instances,
                params=params,
                response=resp
            ))
        except Exception as e:
            print(e)
            pass
    return result