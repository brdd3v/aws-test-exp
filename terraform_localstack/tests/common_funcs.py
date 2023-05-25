import boto3
import json
import os
import sys


def get_client(service):
    client = boto3.client(service,
                          endpoint_url="http://localhost:4566",
                          region_name="eu-central-1",
                          use_ssl=False,
                          verify=False)
    return client


def get_resource_config(filename):
    with open(f"{sys.path[0]}/{filename}", "r") as json_file:
        json_data = json.loads(json_file.read())["Config"]
        return json_data


def delete_logs():
    log_group_name = "/aws/lambda/lambda-func-exp-1"
    client = get_client(service="logs")
    log_streams_resp = client.describe_log_streams(logGroupName=log_group_name)
    for log_stream in log_streams_resp["logStreams"]:
        client.delete_log_stream(logGroupName=log_group_name,
                                 logStreamName=log_stream["logStreamName"])


def delete_objects():
    bucket = "bucket-abc-xyz-exp-1"
    client = get_client(service="s3")
    resp = client.list_objects(Bucket=bucket)
    if "Contents" in resp:
        objects = [el["Key"] for el in resp["Contents"]]
        for el in objects:
            client.delete_object(Bucket=bucket, Key=el)


def upload_sample_data():
    bucket = "bucket-abc-xyz-exp-1"
    client = get_client(service="s3")
    res = [el for el in os.scandir(f"{sys.path[0]}/data")]
    for sample_file in res:
        client.upload_file(sample_file.path, bucket, sample_file.name)
