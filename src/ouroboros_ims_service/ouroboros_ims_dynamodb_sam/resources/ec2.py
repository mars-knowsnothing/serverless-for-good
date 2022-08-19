import json
import os
import boto3
import decimal
import ipaddress
import traceback
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key, Attr
from datetime import datetime, timezone, timedelta
from . import Resource

class Instance(Resource):
    
    def __init__(self, *args, **kwargs):
        super().__init__(name="ec2.instances",*args, **kwargs)
        
        self.register_apis(
            [
                {
                    "resource":"/resources/ec2/instances",
                    "httpMethod":"GET",
                    "func":"list"
                },
                {
                    "resource":"/resources/ec2/instances",
                    "httpMethod":"POST",
                    "func":"create"
                }
            ]
        )

    def register_apis(self,APIs):
        for api in APIs:
            self.Register(api["resource"],api["httpMethod"],getattr(self,api["func"]))

    def get(self):
        return
    
    def list(self,event, **kwargs):
        scan_params = dict()
        filters = event.get("filters")
        if filters:
            scan_params["FilterExpression"]=self.DynamoDBFilters(filters)
        data = list()
        # print(scan_params)
        response = self.table.scan(
            **scan_params
        )
        data.extend(response['Items'])
        while 'LastEvaluatedKey' in response:
            response = self.table.scan(ExclusiveStartKey=response['LastEvaluatedKey'],**scan_params)
            data.extend(response['Items'])
        return dict(
            code=200,
            data=data
        )

    
    def create(self,event:dict) -> dict:
        try:
            now = datetime.utcnow().astimezone(self.TIME_ZONE)
            updated_at = now.strftime("%Y-%m-%d %H:%M:%S")
            Item = event["payload"]
            _ = Item.copy()
            _["updatedAt"] = updated_at
            # _["appId"]=self.get_logical_id(Item["projectCode"],Item["platform"],Item["envName"],Item["appName"])
            response = self.table.put_item(
                Item=_,
                ConditionExpression = "attribute_not_exists(InstanceId)"
            )
            data = {
                "request":{
                    "Item":_
                },
                "response":{
                    "HTTPStatusCode":response["ResponseMetadata"]["HTTPStatusCode"],
                    "RequestId":response["ResponseMetadata"]["RequestId"]
                }
            }
            return dict(
                code=response["ResponseMetadata"]["HTTPStatusCode"],
                data=data
            )
        except ClientError as ce:
            return dict(
                code=ce.response["ResponseMetadata"]["HTTPStatusCode"],
                data=ce.response['Error'],
                messages=[ce.response["Error"]["Message"]]
            )
    
    def delete(self):
        return
    
    def update(self):
        return

