import json
from utilities.complex_encoder import ComplexEncoder
from utilities.constants import MS_RESPONSE_SCHEMA

class APIGatewayResponse(object):
    def __init__(self, cookies=None, isBase64Encoded=False, statusCode=200, headers=None, **kwargs) -> None:
        self.cookies = cookies
        self.isBase64Encoded = isBase64Encoded
        self.statusCode = statusCode
        self.headers = headers
        for k in MS_RESPONSE_SCHEMA.keys():
            if kwargs.get(k):
                setattr(self,k,kwargs[k])
    def json(self):
        _json_output = dict(
            statusCode=self.statusCode
        )
        _body = dict()
        for key in ["data", "messages"]:
            _prop = getattr(self, key, [])
            # if _prop:
            _body[key] = _prop
        _json_output["body"] = json.dumps(_body,cls=ComplexEncoder)
        return _json_output