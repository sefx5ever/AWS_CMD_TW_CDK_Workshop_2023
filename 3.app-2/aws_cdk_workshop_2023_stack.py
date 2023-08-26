from aws_cdk import (
    Stack, CfnOutput,
    aws_ec2 as ec2,
    aws_secretsmanager as secretsmanager,
    aws_rds as rds
)
from constructs import Construct
import json

class AwsCdkWorkshop2023Stack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        USER_NAME = "wyne"
        # App 3：EC2 + Database in VPC

        ## Create a self-defined vpc
        vpc = ec2.Vpc(self, f"aws-cmd-vpc-{USER_NAME}",
            ip_addresses=ec2.IpAddresses.cidr("10.0.0.0/16"),
            availability_zones=["us-east-1a","us-east-1b"],
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name=f"aws-cmd-pub-sub-{USER_NAME}",
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=24
                ),
                ec2.SubnetConfiguration(
                    name=f"aws-cmd-pri-sub-{USER_NAME}",
                    subnet_type=ec2.SubnetType.PRIVATE_ISOLATED,
                    cidr_mask=24
                )
            ],
            vpc_name=f"aws-cmd-vpc-{USER_NAME}"
        )

        ### [Caution | VPC] :
        # If you purpose to modify the exists subnet in the module 
        # of Vpc after first built, such as unplug the NAT Gateway
        # or change the rule of security group and etc., please 
        # destroy the stack first then only rebuild the latest stack.
        ### 

        ### [Reference] :
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_ec2/Vpc.html

        ## Create the security group for HTTP/HTTPS access
        aws_cmd_sg_http = ec2.SecurityGroup(self, "aws_cmd_sg_http",
            vpc=vpc,
            description="Allow traffic access through HTTP/HTTPS",
            allow_all_outbound=True
        )
        aws_cmd_sg_http.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(80), "Allow ssh access from the world")

        ### [Reference] :
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_ec2/README.html#allowing-connections

        ## Read the shell script for EC2's user data
        with open("./setup.sh","r") as file:
            self.user_data = file.read()

        ## Create an EC2 of Amazon Linux 2 Instance 
        aws_cmd_ec2_1 = ec2.Instance(self, "aws_cmd_ec2_1",
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
            instance_type=ec2.InstanceType.of(
                instance_class=ec2.InstanceClass.T2,
                instance_size=ec2.InstanceSize.MICRO
            ),
            machine_image=ec2.MachineImage.latest_amazon_linux2(),
            security_group=aws_cmd_sg_http,
            user_data=ec2.UserData.custom(self.user_data)
        )

        ### [Reference] :
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_ec2/UserData.html

        ## Create an RDS Instance Postgres's database
        # Templated secret with username and password fields
        templated_secret = secretsmanager.Secret(self, "TemplatedSecret",
            generate_secret_string=secretsmanager.SecretStringGenerator(
                secret_string_template=json.dumps({"username": "aws_cmd_rds_admin"}),
                generate_string_key="aws_cmd_rds_password"
            )
        )
        # Using the templated secret as credentials
        aws_cmd_rds_postgres = rds.DatabaseInstance(self, f"aws_cmd_rds_{USER_NAME}",
            engine=rds.DatabaseInstanceEngine.POSTGRES,
            credentials=rds.Credentials.from_secret(templated_secret),
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_group_name=f"aws-cmd-pri-sub-{USER_NAME}")
        )

        ### [Reference] :
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_rds/README.html#starting-an-instance-database

        CfnOutput(self, f"[EC2] PublicIP(aws_cmd_ec2_1)", value=aws_cmd_ec2_1.instance_public_ip)
        CfnOutput(self, "[RDS] MySQL Access Endpoint", value=aws_cmd_rds_postgres.db_instance_endpoint_address)
        CfnOutput(self, "[RDS] MySQL Endpoint Port", value=aws_cmd_rds_postgres.db_instance_endpoint_port)