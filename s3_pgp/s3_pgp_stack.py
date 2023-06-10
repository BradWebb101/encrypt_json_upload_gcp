from aws_cdk import core
import aws_cdk.aws_s3 as s3
import aws_cdk.aws_lambda as _lambda
import aws_cdk.aws_s3_notifications as s3n
from aws_cdk.aws_s3_deployment import BucketDeployment, Source
import aws_cdk.aws_sns as sns


class MyStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create an S3 bucket
        bucket = s3.Bucket(self, "MyBucket",
                           bucket_name=f"{kwargs['name']}-bucket",
                           versioned=True,
                           block_public_access=s3.BlockPublicAccess.BLOCK_ALL)
        
         # Create an SNS topic
        topic = sns.Topic(self, "MyTopic")
        
        # Create a Lambda function
        encrypt_upload_lambda = _lambda.Function(self, "MyLambda",
                                     runtime=_lambda.Runtime.PYTHON_3_9,
                                     handler="index.lambda_handler",
                                     code=_lambda.Code.from_asset("lambda"),
                                     environment={'TOPIC_ARN':topic.topic_arn}
                                     )
        
        bucket.add_event_notification(s3.EventType.OBJECT_CREATED, s3n.LambdaDestination(encrypt_upload_lambda), prefix='/files')
        bucket.grant_read(encrypt_upload_lambda)

        # Add a subscription to the topic (e.g., email subscription)
        topic.add_subscription(sns.Subscription(
            endpoint=kwargs['email'],
            protocol=sns.SubscriptionProtocol.EMAIL
        ))

        # Usage of BucketDeployment
        deployment = BucketDeployment(self, f"{kwargs['name']}Deployment",
                                    sources=[Source.asset("../keys")],
                                    destination_bucket=bucket,
                                    destination_key_prefix='/keys')

       