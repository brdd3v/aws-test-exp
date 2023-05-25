from aws_cdk import (
    aws_iam as iam,
    aws_lambda as lambda_,
    aws_s3 as s3,
    aws_s3_notifications as s3n,
    aws_logs,
    CfnParameter,
    RemovalPolicy,
    Stack,
)
from constructs import Construct


class CdkStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        param_bucket_name = CfnParameter(self, "ParamBucketName",
                                         default="bucket-abc-xyz-exp-5")
        param_function_name = CfnParameter(self, "ParamFunctionName",
                                           default="lambda-func-exp-5")

        iam_for_lambda = iam.Role(self, "iam_for_lambda",
                                  role_name="iam_for_lambda-exp-5",
                                  assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"))

        iam_for_lambda.add_to_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=["logs:CreateLogGroup", 
                     "logs:CreateLogStream", 
                     "logs:PutLogEvents"],
            resources=["arn:aws:logs:*:*:*"]))

        iam_for_lambda.add_to_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=["s3:GetObject"],
            resources=[f"arn:aws:s3:::{param_bucket_name.value_as_string}/*"]))

        lambda_func = lambda_.Function(self, "lambda",
                                       function_name=param_function_name.value_as_string,
                                       runtime=lambda_.Runtime.PYTHON_3_9,
                                       role=iam_for_lambda,
                                       handler='lambda_func.lambda_handler',
                                       code=lambda_.Code.from_asset('lambda_func'))

        bucket = s3.Bucket(self, "bucket", 
                           bucket_name=param_bucket_name.value_as_string,
                           auto_delete_objects=True,
                           removal_policy=RemovalPolicy.DESTROY)
        
        bucket.add_event_notification(s3.EventType.OBJECT_CREATED,
                                      s3n.LambdaDestination(lambda_func))

        cfn_permission = lambda_.CfnPermission(self, "lambda_permission",
                                               function_name=lambda_func.function_name,
                                               action="lambda:InvokeFunction",
                                               principal="s3.amazonaws.com",
                                               source_arn=bucket.bucket_arn)

        lambda_log_group = aws_logs.CfnLogGroup(self, "lambda_log_group",
                                                log_group_name=f"/aws/lambda/{param_function_name.value_as_string}",
                                                retention_in_days=14)
