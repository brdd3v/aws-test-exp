#!/usr/bin/env python

import boto3
import json
import time


bucket_name = "bucket-abc-xyz-exp-6"
function_name = "lambda-func-exp-6"
role_name = "iam_for_lambda-exp-6"


assume_role_policy = {
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


lambda_logging_policy = {
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


lambda_s3_policy = {
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject"
      ],
      "Resource": f"arn:aws:s3:::{bucket_name}/*"
    }
  ]
}


def get_zip_file_data():
    with open("./lambda_func.zip", "rb") as file_data:
        return file_data.read()


def main():
    s3_client = boto3.client("s3")
    s3_client.create_bucket(Bucket=bucket_name,
                            CreateBucketConfiguration={'LocationConstraint': 'eu-central-1'})
    s3_client.put_bucket_tagging(
        Bucket=bucket_name,
        Tagging={
            "TagSet": [
                {
                    "Key": "Env",
                    "Value": "Dev"
                },
                {
                    "Key": "Owner",
                    "Value": "AWSPythonSDK"
                }
            ]
        }
    )
    print(f"S3 Bucket created: {bucket_name}")

    iam_client = boto3.client("iam")
    role_resp = iam_client.create_role(
        RoleName=role_name,
        AssumeRolePolicyDocument=json.dumps(assume_role_policy),
        Tags=[
            {
                "Key": "Env",
                "Value": "Dev"
            },
            {
                "Key": "Owner",
                "Value": "AWSPythonSDK"
            }
        ]
    )
    print(f"IAM Role created: {role_name}")

    policy_logging_resp = iam_client.create_policy(
        PolicyName="lambda_logging-exp-6",
        PolicyDocument=json.dumps(lambda_logging_policy),
        Tags=[
            {
                "Key": "Env",
                "Value": "Dev"
            },
            {
                "Key": "Owner",
                "Value": "AWSPythonSDK"
            }
        ]
    )
    print("Policy created: lambda_logging-exp-6")

    policy_s3_resp = iam_client.create_policy(
        PolicyName="lambda_s3-exp-6",
        PolicyDocument=json.dumps(lambda_s3_policy),
        Tags=[
            {
                "Key": "Env",
                "Value": "Dev"
            },
            {
                "Key": "Owner",
                "Value": "AWSPythonSDK"
            }
        ]
    )
    print("Policy created: lambda_s3-exp-6")

    iam_client.attach_role_policy(
        RoleName=role_name,
        PolicyArn=policy_logging_resp["Policy"]["Arn"]
    )

    iam_client.attach_role_policy(
        RoleName=role_name,
        PolicyArn=policy_s3_resp["Policy"]["Arn"]
    )

    time.sleep(15)  # To get around the error: (InvalidParameterValueException) \
    # The role defined for the function cannot be assumed by Lambda

    lambda_client = boto3.client("lambda")
    lambda_resp = lambda_client.create_function(
        FunctionName=function_name,
        Code={"ZipFile": get_zip_file_data()},
        Runtime="python3.9",
        Handler="lambda_func.lambda_handler",
        Role=role_resp["Role"]["Arn"],
        Tags={
            "Env": "Dev",
            "Owner": "AWSPythonSDK"
        }
    )
    lambda_client.add_permission(
        FunctionName=function_name,
        StatementId="AllowExecutionFromS3Bucket",
        Action="lambda:InvokeFunction",
        Principal="s3.amazonaws.com",
        SourceArn=f"arn:aws:s3:::{bucket_name}"
    )
    print(f"Lambda Func created: {function_name}")

    logs_client = boto3.client('logs')
    logs_client.create_log_group(
        logGroupName=f"/aws/lambda/{function_name}",
        tags={
            "Env": "Dev",
            "Owner": "AWSPythonSDK"
        }
    )
    logs_client.put_retention_policy(
        logGroupName=f"/aws/lambda/{function_name}",
        retentionInDays=14
    )
    print(f"Log Group created: /aws/lambda/{function_name}")

    s3_client.put_bucket_notification_configuration(
        Bucket=bucket_name,
        NotificationConfiguration={
            "LambdaFunctionConfigurations": [
                {
                    "LambdaFunctionArn": lambda_resp["FunctionArn"],
                    "Events": ["s3:ObjectCreated:*"]
                }
            ]
        }
    )


if __name__ == "__main__":
    main()
