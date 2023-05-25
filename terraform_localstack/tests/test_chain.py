import time
import pytest

import common_funcs


@pytest.fixture()
def client(request):
    return common_funcs.get_client(request.param)


@pytest.fixture()
def load_sample_data():
    common_funcs.upload_sample_data()  # s3 -> lambda


def setup():
    common_funcs.delete_objects()
    common_funcs.delete_logs()


@pytest.mark.parametrize("client", ["s3"], indirect=True)
def test_s3_no_data(client):
    resp = client.list_objects(Bucket="bucket-abc-xyz-exp-1")
    assert "Contents" not in resp


@pytest.mark.parametrize("client", ["logs"], indirect=True)
def test_logs_no_data(client):
    resp = client.describe_log_streams(logGroupName="/aws/lambda/lambda-func-exp-1")
    assert len(resp["logStreams"]) == 0


@pytest.mark.parametrize("client", ["s3"], indirect=True)
@pytest.mark.usefixtures("load_sample_data")
def test_s3_data(client):
    resp = client.list_objects(Bucket="bucket-abc-xyz-exp-1")
    assert len(resp["Contents"]) == 3


@pytest.mark.parametrize("client", ["logs"], indirect=True)
def test_logs_data(client):
    log_group = "/aws/lambda/lambda-func-exp-1"
    time.sleep(5)  # waiting for logs to appear
    resp = client.describe_log_streams(logGroupName=log_group)
    assert len(resp["logStreams"]) == 3
    matches = 0
    for log_stream in resp["logStreams"]:
        log_stream_events = client.get_log_events(logGroupName=log_group,
                                                  logStreamName=log_stream["logStreamName"])
        events = [event["message"] for event in log_stream_events["events"]]
        for event in events:
            matches += 1 if "ContentType" in event else 0
    assert matches == 3


def teardown():
    common_funcs.delete_objects()
    common_funcs.delete_logs()
