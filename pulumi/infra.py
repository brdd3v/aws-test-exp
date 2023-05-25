"""An AWS Python Pulumi program"""

import json
import pulumi
import pulumi_aws as aws

suffix = "exp-4"
lambda_func_name = f"lambda-func-{suffix}"
tags = {"Env": "Dev", "Owner": "PulumiProviders"}


bucket = aws.s3.Bucket(
    "bucket",
    bucket=f"bucket-abc-xyz-{suffix}",
    force_destroy=True,
    tags=tags
)

iam_for_lambda = aws.iam.Role(
    "iam_for_lambda",
    name=f"iam_for_lambda-{suffix}",
    tags=tags,
    assume_role_policy=json.dumps(
    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "lambda.amazonaws.com",
                },
                "Action": "sts:AssumeRole"
            }
        ]
    })
)

policy_lambda_logging = aws.iam.Policy(
    "lambda_logging",
    name=f"lambda_logging-{suffix}",
    tags=tags,
    policy=json.dumps(
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
    })
)

policy_lambda_s3 = aws.iam.Policy(
    "lambda_s3",
    name=f"lambda_s3-{suffix}",
    tags=tags,
    policy=bucket.arn.apply(
        lambda arn: json.dumps(
            {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Action": [
                            "s3:GetObject"
                        ],
                        "Resource": f"{arn}/*"
                    }
                ]
            }
        )
    )
)

policy_attachment_logs = aws.iam.RolePolicyAttachment(
    "policy_attachment_logs",
    role=iam_for_lambda.name,
    policy_arn=policy_lambda_logging.arn
)

policy_attachment_s3 = aws.iam.RolePolicyAttachment(
    "policy_attachment_s3",
    role=iam_for_lambda.name,
    policy_arn=policy_lambda_s3.arn
)

lambda_func = aws.lambda_.Function(
    "lambda",
    name=lambda_func_name,
    code=pulumi.AssetArchive({
        ".": pulumi.FileArchive("./lambda_func"),
    }),
    runtime="python3.9",
    role=iam_for_lambda.arn,
    handler="lambda_func.lambda_handler",
    tags=tags
)

lambda_permission = aws.lambda_.Permission(
    "lambda_permission",
    statement_id="AllowExecutionFromS3Bucket",
    action="lambda:InvokeFunction",
    function=lambda_func.arn,
    principal="s3.amazonaws.com",
    source_arn=bucket.arn
)

bucket_notification = aws.s3.BucketNotification(
    "bucket_notification",
    bucket=bucket.id,
    lambda_functions=[
        aws.s3.BucketNotificationLambdaFunctionArgs(
            lambda_function_arn=lambda_func.arn,
            events=["s3:ObjectCreated:*"]
        )
    ],
    opts=pulumi.ResourceOptions(
        depends_on=[lambda_permission]
    )
)

lambda_log_group = aws.cloudwatch.LogGroup(
    "lambda_log_group",
    name=f"/aws/lambda/{lambda_func_name}",
    retention_in_days=14,
    tags=tags
)
