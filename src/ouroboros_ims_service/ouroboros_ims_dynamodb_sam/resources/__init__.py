import os
import json
import boto3
import traceback
import uuid
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key, Attr
from datetime import datetime, timezone, timedelta

dynamodb = boto3.resource('dynamodb')

class Resource(object):

    def __init__(self, *args, **kwargs):
        self.name = kwargs.get("name","resource").replace(".","_")
        self.stage = os.getenv("stage","dev")
        try:
            self.table = dynamodb.Table('cmdb_{stage}_{name}'.format(stage=self.stage,name=self.name))
        except Exception as e:
            print(e)
            raise e
        self.TIME_ZONE = timezone(timedelta(hours=8))
        self._handlers = {}
        self.API_GATEWAY_RESPONSE_SCHEMA = {
            "cookies" : [type("cookie1"),type("cookie2")],
            "isBase64Encoded": type(True),
            # "statusCode": type(200),
            "headers": type({"headername":"headervalue"}),
            # "body": type(json.dumps({"key":"value"}))
        }

    def get_logical_id(self,resourceName):
        pattern = resourceName.lower()
        logical_id = uuid.uuid5(uuid.NAMESPACE_OID,pattern).hex
        return logical_id

    def API(self,event,options=None):
        resource = event["resource"]
        httpMethod = event["httpMethod"]
        handler = self._handlers.get(resource).get(httpMethod)
        api_gateway_event = dict()

        pathParameters=event.get("pathParameters")
        if not pathParameters:
            pathParameters=dict()
        api_gateway_event["resources"]=pathParameters

        queryStringParameters=event.get("queryStringParameters")
        if not queryStringParameters:
            queryStringParameters=dict()
        api_gateway_event["filters"]=queryStringParameters

        payload = event.get("body")
        if not payload:
            payload=json.dumps(dict())
        payload=json.loads(payload)
        api_gateway_event["payload"]=payload
        try:
            resp = handler(event=api_gateway_event)
        except ClientError as ce:
            resp =  dict(
                code=ce.response["ResponseMetadata"]["HTTPStatusCode"],
                data=ce.response['Error'],
                messages=[ce.response["Error"]["Message"]]
            )
        # add cors headers
        resp.update({"headers":{
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,DELETE,PUT'
        }})
        return self.Response(resp)

    def DynamoDBFilters(self,queryStringParameters):
        FilterExpression = None
        for f,v in queryStringParameters.items():
            if not FilterExpression:
                if f.endswith(".contains"):
                    FilterExpression=Attr(f.split('.contains')[0]).contains(v)
                elif f.endswith(".notcontains"):
                    FilterExpression = ~Attr(f.split('.notcontains')[0]).contains(v.split(',')[0])
                    for item in v.split(',')[1:]:
                        FilterExpression=FilterExpression & ~Attr(f.split('.notcontains')[0]).contains(item)
                else:
                    FilterExpression=Attr(f).eq(v)
            else:
                if f.endswith(".contains"):
                    FilterExpression=FilterExpression & Attr(f.split('.contains')[0]).contains(v)
                elif f.endswith(".notcontains"):
                    for item in v.split(','):
                        FilterExpression=FilterExpression & ~Attr(f.split('.notcontains')[0]).contains(item)
                else:
                    FilterExpression=FilterExpression & Attr(f).eq(v)
        return FilterExpression

    def Response(self,handlerResponse):
        _resp = dict()
        _resp["statusCode"] = handlerResponse.get("code",200)
        _resp_body_json = dict(
            data=handlerResponse.get("data",[]),
            messages=handlerResponse.get("messages",[])
        )
        _resp["body"] = json.dumps(_resp_body_json)
        for key in self.API_GATEWAY_RESPONSE_SCHEMA.keys():
            if key in handlerResponse:
                _resp[key]=handlerResponse[key]
        return _resp
    
    def Register(self,resource,httpMethod,func):
        if not self._handlers.get(resource):
            self._handlers[resource] = {
                httpMethod:func
            }
        else:
            self._handlers[resource].update({
                httpMethod:func
            })