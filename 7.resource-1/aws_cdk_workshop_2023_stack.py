from aws_cdk import (
    Stack, CfnOutput,
    aws_s3 as s3,
    aws_s3_deployment as s3deploy,
)
from constructs import Construct

class AwsCdkWorkshop2023Stack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        USER_NAME = "wyne"
        
        website_bucket = s3.Bucket(self, f"aws-cmd-s3-test-{USER_NAME}",
            website_index_document="index.html",
            public_read_access=True
        )

        s3deploy.BucketDeployment(self, f"aws-cmd-s3-deploy-{USER_NAME}",
            sources=[s3deploy.Source.asset("./frontend")],
            destination_bucket=website_bucket,
            destination_key_prefix=""
        )