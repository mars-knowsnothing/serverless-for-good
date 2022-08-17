import json
import botocore
from utilities.aws import AWSUtils

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
        utils = AWSUtils(region_name="ap-southeast-1",role_arn="arn:aws:iam::592336536196:role/ouroboros_ims_master")
        print("---record---")
        print(record)
        print("---record---")
    return result