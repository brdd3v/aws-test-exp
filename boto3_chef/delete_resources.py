#!/usr/bin/env python

import boto3


bucket_name = "bucket-abc-xyz-exp-6"
function_name = "lambda-func-exp-6"
role_name = "iam_for_lambda-exp-6"


def get_account_id():
    sts_client = boto3.client("sts")
    return sts_client.get_caller_identity()["Account"]


def main():
    # S3
    s3_client = boto3.client("s3")
    s3_client.delete_bucket(
        Bucket=bucket_name
    )
    print(f"S3 Bucket deleted: {bucket_name}")

    # Logs
    logs_client = boto3.client('logs')
    logs_client.delete_log_group(
        logGroupName=f"/aws/lambda/{function_name}"
    )
    print(f"Log Group deleted: /aws/lambda/{function_name}")

    # Lambda
    lambda_client = boto3.client("lambda")
    lambda_client.delete_function(
        FunctionName=function_name
    )
    print(f"Lambda Func deleted: {function_name}")

    # IAM
    iam_client = boto3.client("iam")
    iam_client.detach_role_policy(
        RoleName=role_name,
        PolicyArn=f"arn:aws:iam::{get_account_id()}:policy/lambda_logging-exp-6"
    )
    iam_client.detach_role_policy(
        RoleName=role_name,
        PolicyArn=f"arn:aws:iam::{get_account_id()}:policy/lambda_s3-exp-6"
    )

    iam_client.delete_role(
        RoleName=role_name
    )
    print(f"IAM Role deleted: {role_name}")
     
    iam_client.delete_policy(
        PolicyArn=f"arn:aws:iam::{get_account_id()}:policy/lambda_logging-exp-6"
    )
    print("Policy deleted: lambda_logging-exp-6")

    iam_client.delete_policy(
        PolicyArn=f"arn:aws:iam::{get_account_id()}:policy/lambda_s3-exp-6"
    )
    print("Policy deleted: lambda_s3-exp-6")


if __name__ == "__main__":
    main()
