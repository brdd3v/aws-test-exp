import boto3
from typing import Any, Dict
from aws_lambda_powertools.utilities.data_classes import S3Event
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.utilities.validation import validator

from src.schemas import INPUT_SCHEMA, OUTPUT_SCHEMA


s3_client = boto3.client('s3')


@validator(inbound_schema=INPUT_SCHEMA, outbound_schema=OUTPUT_SCHEMA)
def lambda_handler(event: S3Event, context: LambdaContext) -> Dict[str, Any]:

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
