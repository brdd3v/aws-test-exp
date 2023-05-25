from troposphere import GetAtt, Ref, Sub, Parameter, Template, Tags
from troposphere.s3 import Bucket, NotificationConfiguration, LambdaConfigurations
from troposphere.awslambda import Code, Function, Permission
from troposphere.iam import Role, Policy
from troposphere.logs import LogGroup


code = """import boto3


s3_client = boto3.client('s3', region_name="eu-central-1")


def lambda_handler(event, context):
    # Get the object from the event and show its content type
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']

    status = "OK"
    content_type = "text/plain"
    try:
        response = s3_client.get_object(Bucket=bucket, Key=key)
        content_type = response['ContentType']
        print(f"Key = {key}, ContentType = {content_type}")
    except Exception as e:
        print(e)
        print(f"Error getting object '{key}' from bucket '{bucket}'.")
        status = "Error"
        content_type = ""
    finally:
        return {"status": status, "key": key, "content_type": content_type}
"""


def main():
    tags = Tags(Env="Dev", Owner="AWSCF")

    t = Template()
    t.set_version("2010-09-09")


    ParamBucketName = t.add_parameter(
        Parameter("ParamBucketName", Type="String", Default="bucket-abc-xyz-exp-3")
    )

    ParamFunctionName = t.add_parameter(
        Parameter("ParamFunctionName", Type="String", Default="lambda-func-exp-3")
    )


    lambda_iam_role = t.add_resource(
        Role(
            "LambdaIAMRole",
            RoleName="iam_for_lambda-exp-3",
            AssumeRolePolicyDocument={
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Action": ["sts:AssumeRole"],
                        "Effect": "Allow",
                        "Principal": {"Service": ["lambda.amazonaws.com"]},
                    }
                ]
            },
            Policies=[
                Policy(
                    PolicyName="lambda_logging-exp-3",
                    PolicyDocument={
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
                            }
                        ]
                    }
                ),
                Policy(
                    PolicyName="lambda_s3-exp-3",
                    PolicyDocument={
                        "Version": "2012-10-17",
                        "Statement": [
                            {
                                "Action": ["s3:GetObject"],
                                "Effect": "Allow",
                                "Resource": Sub('arn:aws:s3:::${ParamBucketName}/*')
                            }
                        ]
                    }
                )
            ],
            Tags=tags
        )
    )

    lambda_func = t.add_resource(
        Function(
            "LambdaFunction",
            FunctionName=Ref(ParamFunctionName),
            Code=Code(ZipFile=code),
            Handler="index.lambda_handler",
            Role=GetAtt(lambda_iam_role, "Arn"),
            Runtime="python3.9",
            Tags=tags
        )
    )

    lambda_permission = t.add_resource(
        Permission(
            "LambdaPermission",
            FunctionName=Ref(lambda_func),
            Action="lambda:InvokeFunction",
            Principal="s3.amazonaws.com",
            SourceArn=Sub('arn:aws:s3:::${ParamBucketName}')
        )
    )

    s3_bucket = t.add_resource(
        Bucket(
            "S3Bucket",
            BucketName=Ref(ParamBucketName),
            DependsOn=[lambda_permission],
            NotificationConfiguration=NotificationConfiguration(
                LambdaConfigurations=[
                    LambdaConfigurations(
                        Event="s3:ObjectCreated:*",
                        Function=GetAtt(lambda_func, "Arn")
                    )
                ]
            ),
            Tags=tags
        )    
    )

    log_group = t.add_resource(
        LogGroup(
            "LogGroup",
            LogGroupName=Sub('/aws/lambda/${ParamFunctionName}'),
            RetentionInDays=14,
            Tags=tags
        )
    )


    with open("resources_gen.yml", "w") as f:
        f.write(t.to_yaml())

    with open("resources_gen.json", "w") as f:
        f.write(t.to_json())


if __name__ == "__main__":
    main()
