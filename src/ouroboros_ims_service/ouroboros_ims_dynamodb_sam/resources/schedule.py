import decimal
import json
import os
import resource
import boto3
import decimal
import ipaddress
import traceback
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key, Attr
from datetime import datetime, timezone, timedelta
from . import Resource


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            # wanted a simple yield str(o) in the next line,
            # but that would mean a yield on the line with super(...),
            # which wouldn't work (see my comment below), so...
            if str(o) == str(int(o)):
                return int(o)
            else:
                return float(o)
        return super(DecimalEncoder, self).default(o)

class Log(Resource):
    def __init__(self, *args, **kwargs):
        super().__init__(name="schedule.logs", *args, **kwargs)
        self.register_apis(
            [
                {
                    "resource": "/resources/schedule/logs",
                    "httpMethod": "GET",
                    "func": "list"
                }
            ]
        )

    def register_apis(self, APIs):
        for api in APIs:
            self.Register(api["resource"], api["httpMethod"],
                          getattr(self, api["func"]))

    def list(self, event, **kwargs):
        scan_params = dict()
        filters = event.get("filters")
        if filters:
            scan_params["FilterExpression"] = self.DynamoDBFilters(filters)
        data = list()
        # print(scan_params)
        response = self.table.scan(
            **scan_params
        )
        data.extend(response['Items'])
        while 'LastEvaluatedKey' in response:
            response = self.table.scan(
                ExclusiveStartKey=response['LastEvaluatedKey'], **scan_params)
            data.extend(response['Items'])
        return dict(
            code=200,
            data=json.loads(json.dumps(data,cls=DecimalEncoder))
        )


class Rule(Resource):

    def __init__(self, *args, **kwargs):
        super().__init__(name="schedule.rules", *args, **kwargs)

        self.register_apis(
            [
                {
                    "resource": "/resources/schedule/rules",
                    "httpMethod": "GET",
                    "func": "list"
                },
                {
                    "resource": "/resources/schedule/rules",
                    "httpMethod": "POST",
                    "func": "create"
                },
                {
                    "resource": "/resources/schedule/rules/{rule-id}",
                    "httpMethod": "DELETE",
                    "func": "delete"
                }
            ]
        )

    def register_apis(self, APIs):
        for api in APIs:
            self.Register(api["resource"], api["httpMethod"],
                          getattr(self, api["func"]))

    def get(self):
        return

    def list(self, event, **kwargs):
        scan_params = dict()
        filters = event.get("filters")
        if filters:
            scan_params["FilterExpression"] = self.DynamoDBFilters(filters)
        data = list()
        # print(scan_params)
        response = self.table.scan(
            **scan_params
        )
        data.extend(response['Items'])
        while 'LastEvaluatedKey' in response:
            response = self.table.scan(
                ExclusiveStartKey=response['LastEvaluatedKey'], **scan_params)
            data.extend(response['Items'])
        return dict(
            code=200,
            data=data
        )

    def create(self, event: dict) -> dict:
        try:
            now = datetime.utcnow().astimezone(self.TIME_ZONE)
            updated_at = now.strftime("%Y-%m-%d %H:%M:%S")
            Item = event["payload"]
            _ = Item.copy()
            _["ruleId"] = self.get_logical_id(resourceName=_["ruleName"])
            _["updatedAt"] = updated_at
            # _["appId"]=self.get_logical_id(Item["projectCode"],Item["platform"],Item["envName"],Item["appName"])
            response = self.table.put_item(
                Item=_,
                ConditionExpression="attribute_not_exists(ruleId)"
            )
            data = {
                "request": {
                    "Item": _
                },
                "response": {
                    "HTTPStatusCode": response["ResponseMetadata"]["HTTPStatusCode"],
                    "RequestId": response["ResponseMetadata"]["RequestId"]
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

    def delete(self, event: dict) -> dict:
        resource = event["resources"]
        try:
            response = self.table.delete_item(
                Key={
                    "ruleId": resource["rule-id"]
                }
            )
            return dict(
                code=response["ResponseMetadata"]["HTTPStatusCode"],
                data=response
            )
        except ClientError as ce:
            return dict(
                code=ce.response["ResponseMetadata"]["HTTPStatusCode"],
                data=ce.response['Error'],
                messages=[ce.response["Error"]["Message"]]
            )

    def update(self):
        return
