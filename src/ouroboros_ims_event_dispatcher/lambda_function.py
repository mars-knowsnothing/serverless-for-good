from asyncore import dispatcher
import json
from unittest import result
from utilities.aws import AWSUtils

class Dispatcher(object):

    def __init__(self,utils):
        self.utils =utils
        self._handlers = {
            "aws:dynamodb":{}
        }
        self.register(
            resourceType="aws:dynamodb",
            resourceId="cmdb_dev_schedule_rules",
            actionId="INSERT",
            func=self.rule_insert_handler
        )
        self.register(
            resourceType="aws:dynamodb",
            resourceId="cmdb_dev_schedule_rules",
            actionId="REMOVE",
            func=self.rule_remove_handler
        )

    def register(self, resourceType: str,resourceId: str, actionId: str, func: any) -> None:
        if not self._handlers[resourceType].get(resourceId):
            self._handlers[resourceType][resourceId] = {
                actionId: func
            }
        else:
            self._handlers[resourceType][resourceId].update({
                actionId: func
            })
    # Dispatch DynamoDB Event to Handler
    def dispatch(self, record:dict) -> dict:
        eventSource = record["eventSource"]
        eventSourceARN = record["eventSourceARN"]
        eventSourceTable = eventSourceARN.split("/")[1]
        eventName = record["eventName"]
        handler = self._handlers[eventSource].get(eventSourceTable).get(eventName)
        result = handler(
            dict(
                eventSource=eventSource,
                eventSourceTable=eventSourceTable,
                eventName=eventName,
                eventContent=record["dynamodb"]  
            )
        )
        record.update({
            "output":result
        })
        return record
    def rule_remove_handler(self, streamEvent: dict) -> dict:
        result = dict()
        self.utils.logger.info(streamEvent)
        return result

    def rule_insert_handler(self, streamEvent: dict) -> dict:
        self.utils.logger.info(streamEvent)
        result = dict()
        _ = {
            "messageGroupId": streamEvent["eventContent"]["NewImage"]["action"]["S"], #start_instances
            "scheduleExpression": streamEvent["eventContent"]["NewImage"]["scheduleExpression"]["S"],
            "name": streamEvent["eventContent"]["NewImage"]["ruleName"]["S"],
            'targetId': streamEvent["eventContent"]["NewImage"]["targetId"]["S"],
            'targetArn': streamEvent["eventContent"]["NewImage"]["targetArn"]["S"],
            "input": {
                "action":streamEvent["eventContent"]["NewImage"]["action"]["S"],
                "desiredState": {
                    "name":streamEvent["eventContent"]["NewImage"]["desiredState"]["M"]["name"]["S"]
                },
                "filters": {k:v["S"] for k,v in streamEvent["eventContent"]["NewImage"]["filters"]["M"].items()}
            }
        }
        event_put_rule = {
            "QueueUrl":"https://sqs.ap-southeast-1.amazonaws.com/592336536196/sqs_dev_event_bridge_change.fifo",
            "MessageBody":_,
            "MessageGroupId":"event_bridge_put_rule"
        }
        result.update({"put_rule":self.push_event(event_put_rule)})
        return result

    def push_event(self, event: dict) -> dict:
        client = self.utils.client("sqs")
        response = client.send_message(
            QueueUrl=event["QueueUrl"],
            MessageBody=json.dumps(event["MessageBody"]),
            MessageGroupId=event["MessageGroupId"]
        )
        self.utils.logger.info(response)
        return response

def lambda_handler(event, context):
    records = event["Records"]
    result = list()
    utils = AWSUtils(region_name="ap-southeast-1",role_arn="arn:aws:iam::592336536196:role/ouroboros_ims_master")
    dispatcher = Dispatcher(utils)
    for record in records:
        utils.logger.info(record) 
        dispatcher.dispatch(record=record)
    return result
