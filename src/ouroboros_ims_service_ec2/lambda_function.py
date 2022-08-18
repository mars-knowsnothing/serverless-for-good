import json
import botocore
import boto3
from utilities.aws import AWSUtils
from datetime import datetime, timezone, timedelta

TIME_ZONE = timezone(timedelta(hours=8))
dynamodb = boto3.resource('dynamodb')
activity_log_table = dynamodb.Table('cmdb_dev_activity_log')

def log_activity(event):
    now = datetime.utcnow().astimezone(TIME_ZONE)
    updated_at = now.strftime("%Y-%m-%d %H:%M:%S")
    _ = event.copy()
    _["updatedAt"] = updated_at
    response = activity_log_table.put_item(
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
    log_activity(response)
    return response

def stop_instances(utils,InstanceIds, Hibernate=False, Force=False, DryRun=False):
    client = utils.client("ec2")
    response = client.stop_instances(
        InstanceIds=InstanceIds,
        Hibernate=Hibernate,
        DryRun=DryRun,
        Force=Force
    )
    log_activity(response)
    return response

def lambda_handler(event, context):
    # TODO implement
    print(event)
    records = event["Records"]
    result = list()
    for record in records:
        utils = AWSUtils(region_name="ap-southeast-1",role_arn="arn:aws:iam::592336536196:role/ouroboros_ims_master")
        print("---record---")
        print(record)
        params = json.loads(record["body"])
        try:
            instances = describe_instances(utils,filters=params["filters"])
            if params["action"]=="start_instances":
                resp = start_instances(utils,[i["InstanceId"] for i in instances])
            elif params["action"]=="stop_instances":
                resp = stop_instances(utils,[i["InstanceId"] for i in instances])
            print(resp)
            print("---record---")
        except Exception as e:
            print(e)
            pass
    return result