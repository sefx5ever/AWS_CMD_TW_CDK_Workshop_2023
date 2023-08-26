from aws_cdk import (
    Stack, CfnOutput,
    aws_ec2 as ec2
)
from constructs import Construct

class AwsCdkWorkshop2023Stack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        # App 1：EC2 with all default
        USER_NAME = "wyne"

        ## Select the default vpc
        vpc = ec2.Vpc.from_lookup(self, "default-vpc", is_default=True)

        ## Create a security group 
        aws_cmd_sg_http = ec2.SecurityGroup(self, f"aws-cmd-sg-http-{USER_NAME}",
            vpc=vpc,
            description="Allow traffic access through HTTP",
            allow_all_outbound=True
        )
        aws_cmd_sg_http.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(80), "Allow http access from the world")

        ### [Reference] :
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_ec2/README.html#allowing-connections

        ## Read the shell script for EC2's user data
        with open("./setup.sh","r") as file:
            self.user_data = file.read()

        ## Create an EC2 of Amazon Linux 2 Instance 
        aws_cmd_ec2_1 = ec2.Instance(self, f"aws-cmd-ec2-1-{USER_NAME}",
            vpc=vpc,
            instance_type=ec2.InstanceType.of(
                instance_class=ec2.InstanceClass.T3,
                instance_size=ec2.InstanceSize.MICRO
            ),
            security_group=aws_cmd_sg_http,
            machine_image=ec2.MachineImage.latest_amazon_linux2(),
            user_data=ec2.UserData.custom(self.user_data)
        )

        ### [Reference] :
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_ec2/UserData.html

        CfnOutput(self, f"[EC2] PublicIP(aws_cmd_ec2_1)", value=aws_cmd_ec2_1.instance_public_ip)