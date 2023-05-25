import json
import os
import sys
import boto3
import pytest
from moto import mock_s3

sys.path.append('../src')

import src.lambda_func as lambda_func_module  # noqa: E402


@pytest.fixture(scope="function")
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"


@pytest.fixture()
def s3_mock(aws_credentials):
    with mock_s3():
        s3_client = boto3.client("s3", region_name="us-east-1")
        s3_client.create_bucket(Bucket="example-bucket")
        s3_client.put_object(Bucket="example-bucket",
                             Key="test/key",
                             Body="some data",
                             ContentType="text/plain")
        yield s3_client


@pytest.fixture()
def sample_event_ok():
    with open("tests/events/SampleS3Event.json", "r", encoding="utf-8") as json_file:
        yield json.load(json_file)


@pytest.fixture()
def sample_event_error():
    with open("tests/events/SampleS3EventError.json", "r", encoding="utf-8") as json_file:
        yield json.load(json_file)


@pytest.fixture(autouse=True)
def setup_module(s3_mock):
    lambda_func_module.s3_client = s3_mock


def test_lambda_ok(sample_event_ok):
    test_return_value = lambda_func_module.lambda_handler(event=sample_event_ok, context=None)
    assert test_return_value == {"status": "OK", "key": "test/key", "content_type": "text/plain"}


def test_lambda_error(sample_event_error):
    # non-existing bucket
    test_return_value = lambda_func_module.lambda_handler(event=sample_event_error, context=None)
    assert test_return_value == {"status": "Error", "key": "test/key", "content_type": ""}
