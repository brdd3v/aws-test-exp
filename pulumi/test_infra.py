import pulumi
import pytest


def check_tags(tags):
    assert tags == {"Env": "Dev", "Owner": "PulumiProviders"}


class MyMocks(pulumi.runtime.Mocks):
    def new_resource(self, args: pulumi.runtime.MockResourceArgs):
        return [args.name + '_id', args.inputs]
    def call(self, args: pulumi.runtime.MockCallArgs):
        return {}


pulumi.runtime.set_mocks(MyMocks())


import infra


@pulumi.runtime.test
def test_function_name():
    def check_name(name):
        assert name == "lambda-func-exp-4"
    return infra.lambda_func.name.apply(check_name)


@pulumi.runtime.test
def test_function_runtime():
    def check_runtime(rt):
        assert rt == "python3.9"
    return infra.lambda_func.runtime.apply(check_runtime)


@pulumi.runtime.test
def test_function_handler():
    def check_entrypoint(handler):
        import importlib
        from inspect import signature

        module_name, function_handler = handler.split('.', 1)
        module = importlib.import_module(f"lambda_func.{module_name}")
        fn = getattr(module, function_handler)
        assert callable(fn)

        sig = signature(fn)
        assert ['event', 'context'] == list(sig.parameters.keys())
    return infra.lambda_func.handler.apply(check_entrypoint)


@pulumi.runtime.test
def test_function_tags():
    return infra.lambda_func.tags.apply(check_tags)


@pulumi.runtime.test
def test_bucket_name():
    def check_bucket_name(name):
        assert name == "bucket-abc-xyz-exp-4"
    return infra.bucket.bucket.apply(check_bucket_name)


@pulumi.runtime.test
def test_bucket_force_destroy():
    def check_force_destroy(val):
        assert val is True
    return infra.bucket.force_destroy.apply(check_force_destroy)


@pulumi.runtime.test
def test_bucket_tags():
    return infra.bucket.tags.apply(check_tags)


@pulumi.runtime.test
def test_log_group_name():
    def check_log_group_name(name):
        assert name == "/aws/lambda/lambda-func-exp-4"
    return infra.lambda_log_group.name.apply(check_log_group_name)


@pulumi.runtime.test
def test_log_group_tags():
    return infra.lambda_log_group.tags.apply(check_tags)
