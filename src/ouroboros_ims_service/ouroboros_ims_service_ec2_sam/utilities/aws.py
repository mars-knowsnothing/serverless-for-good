import boto3
# from utils import Utils
from utilities.utils import Utils

class AWSUtils(Utils):

    def __init__(self, **kwargs):
        super().__init__()
        self.kwargs = kwargs
        self.region = self.kwargs.get("region_name", "cn-north-1")
        self.credentials = {k: v for k, v in kwargs.items() if k in ["aws_secret_access_key",
                                                                     "aws_access_key_id",
                                                                     "role_arn"
                                                                     ]}
        if self.credentials:
            self.session = self._session()
        else:
            self.session = None

    def client(self, service):
        service_client = getattr(self, "{service}_client".format(service=service), None)
        if not service_client:
            try:
                service_client = self.session.client(service, region_name=self.region)
                setattr(self, "{service}_client".format(service=service), service_client)
            except AttributeError:
                pass
        return service_client

    def _session(self):
        aws_access_key_id = self.credentials.get('aws_access_key_id')
        aws_secret_access_key = self.credentials.get('aws_secret_access_key')
        if self.credentials.get("role_arn"):
            role_arn = self.credentials["role_arn"]
            sts_client = boto3.client('sts',
                                      aws_access_key_id=aws_access_key_id,
                                      aws_secret_access_key=aws_secret_access_key,
                                      region_name=self.region)
            resp_sts = sts_client.assume_role(
                RoleArn=role_arn,
                RoleSessionName=self.kwargs.get('role_session_name',
                                                'role-session-' + super().get_ts()),
            )
            switch_role_session = boto3.Session(
                aws_access_key_id=resp_sts['Credentials']['AccessKeyId'],
                aws_secret_access_key=resp_sts['Credentials']['SecretAccessKey'],
                aws_session_token=resp_sts['Credentials']['SessionToken'],
                region_name=self.region
            )
            return switch_role_session
        else:
            return boto3.Session(aws_access_key_id=aws_access_key_id,
                                 aws_secret_access_key=aws_secret_access_key,
                                 region_name=self.region)