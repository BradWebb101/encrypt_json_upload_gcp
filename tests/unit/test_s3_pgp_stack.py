import aws_cdk as core
import aws_cdk.assertions as assertions

from s3_pgp.s3_pgp_stack import S3PgpStack

# example tests. To run these tests, uncomment this file along with the example
# resource in s3_pgp/s3_pgp_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = S3PgpStack(app, "s3-pgp")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
