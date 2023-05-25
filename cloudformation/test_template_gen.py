import contextlib
import json
import os
import pytest
from cfn_flip import to_json


@pytest.fixture()
def data_resources():
    with open("resources.yml", "r") as yaml_f:
        yield json.loads(to_json(yaml_f.read()))

@pytest.fixture()
def data_resources_gen():
    with open("resources_gen.json", "r") as json_f:
        yield json.loads(json_f.read())


def setup():
    import resources_
    resources_.main()


def test_resources_gen_template(data_resources, data_resources_gen):
    assert data_resources == data_resources_gen


def teardown():
    for filename in ["resources_gen.json", "resources_gen.yml"]:
        with contextlib.suppress(FileNotFoundError):
            os.remove(filename)
