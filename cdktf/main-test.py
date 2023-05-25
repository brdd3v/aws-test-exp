import json
from cdktf import Testing
from cdktf_cdktf_provider_aws import (
    cloudwatch_log_group,
    iam_role,
    iam_policy,
    lambda_function,
    lambda_permission,
    s3_bucket,
    s3_bucket_notification,
    provider
)
from main import MyStack


class TestMain:
    stack = MyStack(Testing.app(), "cdktf")
    synthesized = Testing.synth(stack)

    # Terraform
    def test_check_validity(self):
        assert Testing.to_be_valid_terraform(Testing.full_synth(self.stack))

    # Provider
    def test_provider(self):
        assert Testing.to_have_provider(self.synthesized, provider.AwsProvider.TF_RESOURCE_TYPE)

    def test_provider_properties(self):
        assert Testing.to_have_provider_with_properties(self.synthesized,
                                                 provider.AwsProvider.TF_RESOURCE_TYPE,
                                                 {
                                                     "region": "eu-central-1",
                                                     "default_tags": [
                                                         {"tags": {"Env": "Dev", "Owner": "CDKTF"}}
                                                     ]
                                                 })

    # IAM
    def test_iam_role_properties(self):
        assert Testing.to_have_resource_with_properties(self.synthesized,
                                                        iam_role.IamRole.TF_RESOURCE_TYPE,
                                                        {
                                                            "name": "iam_for_lambda-exp-7",
                                                            "assume_role_policy": json.dumps(
                                                                {
                                                                    "Version": "2012-10-17",
                                                                    "Statement": [
                                                                        {
                                                                        "Effect": "Allow",
                                                                        "Principal": {
                                                                            "Service": "lambda.amazonaws.com"
                                                                        },
                                                                        "Action": "sts:AssumeRole"
                                                                        }
                                                                    ]
                                                                }
                                                            )
                                                        })

    def test_iam_policy_logging_properties(self):
        assert Testing.to_have_resource_with_properties(self.synthesized,
                                                        iam_policy.IamPolicy.TF_RESOURCE_TYPE,
                                                        {
                                                            "name": "lambda_logging-exp-7",
                                                            "policy": json.dumps(
                                                                {
                                                                    "Version": "2012-10-17",
                                                                    "Statement": [
                                                                    {
                                                                        "Effect": "Allow",
                                                                        "Action": [
                                                                        "logs:CreateLogGroup",
                                                                        "logs:CreateLogStream",
                                                                        "logs:PutLogEvents"
                                                                        ],
                                                                        "Resource": "arn:aws:logs:*:*:*"
                                                                    }
                                                                    ]
                                                                }
                                                            )
                                                        })

    def test_iam_policy_s3_properties(self):
        assert Testing.to_have_resource_with_properties(self.synthesized,
                                                        iam_policy.IamPolicy.TF_RESOURCE_TYPE,
                                                        {
                                                            "name": "lambda_s3-exp-7",
                                                            "policy": json.dumps(
                                                                {
                                                                    "Version": "2012-10-17",
                                                                    "Statement": [
                                                                    {
                                                                        "Effect": "Allow",
                                                                        "Action": [
                                                                        "s3:GetObject"
                                                                        ],
                                                                        "Resource": "arn:aws:s3:::bucket-abc-xyz-exp-7/*"
                                                                    }
                                                                    ]
                                                                }
                                                            )
                                                        })

    # Lambda Func
    def test_lambda_func_properties(self):
        assert Testing.to_have_resource_with_properties(self.synthesized,
                                                        lambda_function.LambdaFunction.TF_RESOURCE_TYPE,
                                                        {
                                                            "function_name": "lambda-func-exp-7",
                                                            "handler": "lambda_func.lambda_handler",
                                                            "runtime": "python3.9"
                                                        })

    # Lambda Permission
    def test_lambda_func_permission(self):
        assert Testing.to_have_resource_with_properties(self.synthesized,
                                                        lambda_permission.LambdaPermission.TF_RESOURCE_TYPE,
                                                        {
                                                            "action": "lambda:InvokeFunction",
                                                            "principal": "s3.amazonaws.com"
                                                        })

    # Bucket
    def test_bucket_properties(self):
        assert Testing.to_have_resource_with_properties(self.synthesized,
                                                        s3_bucket.S3Bucket.TF_RESOURCE_TYPE,
                                                        {
                                                            "bucket": "bucket-abc-xyz-exp-7",
                                                            "force_destroy": True
                                                        })

    def test_bucket_notification_properties(self):
        assert Testing.to_have_resource_with_properties(self.synthesized,
                                                        s3_bucket_notification.S3BucketNotification.TF_RESOURCE_TYPE,
                                                        {
                                                            "bucket": "bucket-abc-xyz-exp-7",
                                                            "lambda_function": [{"events": ["s3:ObjectCreated:*"]}]
                                                        })

    # Log Group
    def test_log_group_properties(self):
        assert Testing.to_have_resource_with_properties(self.synthesized,
                                                 cloudwatch_log_group.CloudwatchLogGroup.TF_RESOURCE_TYPE,
                                                 {
                                                     "name": "/aws/lambda/lambda-func-exp-7",
                                                     "retention_in_days": 14
                                                 })

