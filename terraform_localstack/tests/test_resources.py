import pytest
from deepdiff import DeepDiff

import common_funcs


tags = {'Env': 'Dev', 'Owner': 'TFProviders'}

lambda_properties_exclude_paths = [
    "root['FunctionArn']",
    "root['CodeSize']",
    "root['RevisionId']",
    "root['LastModified']",
    "root['CodeSha256']",
    "root['RuntimeVersionConfig']"
]


@pytest.fixture()
def resource_config(request):
    return common_funcs.get_resource_config(request.param)


@pytest.fixture()
def client(request):
    return common_funcs.get_client(request.param)


@pytest.mark.parametrize("client", ["s3"], indirect=True)
def test_s3_bucket(client):
    bucket = "bucket-abc-xyz-exp-1"
    resp = client.list_buckets()
    buckets = [bucket["Name"] for bucket in resp["Buckets"]]
    assert bucket in buckets
    resp = client.get_bucket_notification_configuration(Bucket=bucket)
    funcs = [lambda_config["LambdaFunctionArn"] for lambda_config
             in resp["LambdaFunctionConfigurations"]]
    assert any([func_arn.split(":")[-1] == "lambda-func-exp-1" for func_arn in funcs])
    # Tags
    resp = client.get_bucket_tagging(Bucket=bucket)
    assert {tag["Key"]: tag["Value"] for tag in resp["TagSet"]} == tags


@pytest.mark.parametrize("resource_config, client",
                         [("lambda_config.json", "lambda")],
                         indirect=True)
def test_lambda_func(resource_config, client):
    resp = client.get_function(FunctionName="lambda-func-exp-1")
    diff = DeepDiff(resp["Configuration"],
                    resource_config,
                    exclude_paths=lambda_properties_exclude_paths,
                    ignore_order=True)
    assert not diff
    # Tags
    resp = client.list_tags(Resource=resp["Configuration"]["FunctionArn"])
    assert resp["Tags"] == tags


@pytest.mark.parametrize("client", ["logs"], indirect=True)
def test_logs(client):
    log_group = "/aws/lambda/lambda-func-exp-1"
    resp = client.describe_log_groups()
    log_groups = [group["logGroupName"] for group in resp["logGroups"]]
    assert log_group in log_groups
    # Tags
    resp = client.list_tags_log_group(logGroupName=log_group)
    assert resp["tags"] == tags
