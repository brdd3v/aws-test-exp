#!/usr/bin/env python3
import os

import aws_cdk as cdk

from cdk.cdk_stack import CdkStack


app = cdk.App()
stack = CdkStack(app, "CdkStack")

cdk.Tags.of(stack).add("Env", "Dev")
cdk.Tags.of(stack).add("Owner", "AWSCDK")

app.synth()
