#!/usr/bin/env python

import os
import json
from constructs import Construct
from cdktf import (
    App,
    TerraformStack,
    TerraformAsset,
    AssetType
)
from cdktf_cdktf_provider_aws.provider import (
    AwsProvider,
    AwsProviderDefaultTags
)
from cdktf_cdktf_provider_aws import (
    cloudwatch_log_group,
    iam_role,
    iam_policy,
    iam_policy_attachment,
    lambda_function,
    lambda_permission,
    s3_bucket,
    s3_bucket_notification
)

assume_role_policy = json.dumps(
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

lambda_logging_policy = json.dumps(
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

lambda_s3_policy = json.dumps(
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


class MyStack(TerraformStack):
    def __init__(self, scope: Construct, id: str):
        super().__init__(scope, id)

        AwsProvider(self, "AWS",
                    region="eu-central-1", 
                    default_tags=[
                        AwsProviderDefaultTags(tags={"Env": "Dev",
                                                     "Owner": "CDKTF"})])

        iam_for_lambda = iam_role.IamRole(self, "iam_for_lambda",
                                          name="iam_for_lambda-exp-7",
                                          assume_role_policy=assume_role_policy)
        
        lambda_logging = iam_policy.IamPolicy(self, "lambda_logging",
                                              name="lambda_logging-exp-7",
                                              policy=lambda_logging_policy)

        lambda_s3 = iam_policy.IamPolicy(self, "lambda_s3",
                                         name="lambda_s3-exp-7",
                                         policy=lambda_s3_policy)

        iam_policy_attachment.IamPolicyAttachment(self, "policy_attachment_logs",
                                                  name="policy_attachment_logs",
                                                  roles=[iam_for_lambda.name],
                                                  policy_arn=lambda_logging.arn)

        iam_policy_attachment.IamPolicyAttachment(self, "policy_attachment_s3",
                                                  name="policy_attachment_s3",
                                                  roles=[iam_for_lambda.name],
                                                  policy_arn=lambda_s3.arn)

        asset = TerraformAsset(self, "lambda_file",
                               path = os.path.join(os.getcwd(), "lambda_func"),
                               type = AssetType.ARCHIVE)

        lambda_func = lambda_function.LambdaFunction(self, "lambda",
                                                     filename=asset.path,
                                                     source_code_hash = asset.asset_hash,
                                                     function_name="lambda-func-exp-7",
                                                     role=iam_for_lambda.arn,
                                                     handler="lambda_func.lambda_handler",
                                                     runtime="python3.9")

        bucket = s3_bucket.S3Bucket(self, "bucket",
                                    bucket="bucket-abc-xyz-exp-7",
                                    force_destroy=True)

        lambda_perm = lambda_permission.LambdaPermission(self, "lambda_permission",
                                                         statement_id="AllowExecutionFromS3Bucket",
                                                         action="lambda:InvokeFunction",
                                                         function_name=lambda_func.function_name,
                                                         principal="s3.amazonaws.com",
                                                         source_arn=bucket.arn)

        cloudwatch_log_group.CloudwatchLogGroup(self, "lambda_log_group",
                                                name="/aws/lambda/lambda-func-exp-7",
                                                retention_in_days=14)

        s3_bucket_notification.S3BucketNotification(self, "bucket_notification",
                                                    bucket="bucket-abc-xyz-exp-7",
                                                    lambda_function=[
                                                          s3_bucket_notification.S3BucketNotificationLambdaFunction(
                                                            lambda_function_arn=lambda_func.arn,
                                                            events=["s3:ObjectCreated:*"])],
                                                    depends_on=[lambda_perm])


app = App()
stack = MyStack(app, "cdktf")

app.synth()
