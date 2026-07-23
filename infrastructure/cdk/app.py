#!/usr/bin/env python3
import aws_cdk as cdk
from stacks.troubleshooting_stack import TroubleshootingStack

app = cdk.App()

stack = TroubleshootingStack(
    app,
    "eleknowledge-troubleshooting",
    env=cdk.Environment(
        account="ACCOUNT_ID",
        region="us-east-1"
    ),
    environment="development"
)

app.synth()