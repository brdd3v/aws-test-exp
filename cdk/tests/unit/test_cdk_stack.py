import pytest
import aws_cdk as core
import aws_cdk.assertions as assertions
from aws_cdk.assertions import Match

from cdk_temp.cdk_temp_stack import CdkStack


@pytest.fixture
def template():
    app = core.App()
    stack = CdkStack(app, "CdkStack")
    template = assertions.Template.from_stack(stack)
    yield template


def test_bucket(template):
    template.has_resource_properties(
        "AWS::S3::Bucket",
        {
            "BucketName": {
                "Ref": "ParamBucketName"
            }
        }
    )


def test_bucket_notification(template):
    template.has_resource_properties(
        "Custom::S3BucketNotifications",
        {
            "NotificationConfiguration": {
                "LambdaFunctionConfigurations": [
                    {
                        "Events": [
                            "s3:ObjectCreated:*"
                        ],
                        "LambdaFunctionArn": {
                            "Fn::GetAtt": [
                                Match.any_value(),
                                "Arn"
                            ]
                        }
                    }
                ]
            },
        }
    )


def test_permission(template):
    template.has_resource_properties(
        "AWS::Lambda::Permission",
        {
            "Action": "lambda:InvokeFunction",
            "Principal": "s3.amazonaws.com"
        }
    )


def test_lambda(template):
    template.has_resource_properties(
        "AWS::Lambda::Function",
        {
            "FunctionName": {
                "Ref": "ParamFunctionName"
            },
            "Handler": "lambda_func.lambda_handler",
            "Runtime": "python3.9"
        }
    )


def test_role(template):
    template.has_resource_properties(
        "AWS::IAM::Role",
        {
            "AssumeRolePolicyDocument": {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Action": "sts:AssumeRole",
                        "Effect": "Allow",
                        "Principal": {
                            "Service": "lambda.amazonaws.com"
                        }
                    }
                ]
            }
        }
    )


def test_policies(template):
    template.has_resource_properties(
        "AWS::IAM::Policy",
        {
            "PolicyDocument": {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Action": [
                            "logs:CreateLogGroup",
                            "logs:CreateLogStream",
                            "logs:PutLogEvents"
                        ],
                        "Effect": "Allow",
                        "Resource": "arn:aws:logs:*:*:*"
                    },
                    {
                        "Action": "s3:GetObject",
                        "Effect": "Allow",
                        "Resource": {
                            "Fn::Join": [
                                "",
                                [
                                    "arn:aws:s3:::",
                                    {
                                        "Ref": "ParamBucketName"
                                    },
                                    "/*"
                                ]
                            ]
                        }
                    }
                ]
            },
        }
    )


def test_log_group(template):
    template.has_resource_properties(
        "AWS::Logs::LogGroup",
        {
            "LogGroupName": {
                "Fn::Join": [
                    "",
                    [
                        "/aws/lambda/",
                        {
                            "Ref": "ParamFunctionName"
                        }
                    ]
                ]
            },
            "RetentionInDays": 14
        }
    )
