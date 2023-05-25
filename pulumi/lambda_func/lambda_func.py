import boto3


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
