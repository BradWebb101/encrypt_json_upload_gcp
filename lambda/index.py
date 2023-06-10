import boto3
import gnupg
import os
from google.cloud import storage
import json

s3_client = boto3.client('s3')
gpg = gnupg.GPG()
#Change this so we can switch between prod and nprod with env var/input
storage_client = storage.Client.from_service_account_json('./nproduction_key.json')
sns_client = boto3.client('sns')

def encrypt_and_upload_to_gcp(json_str: str, bucket_name: str, blob_name: str) -> None:
    # Import public key
    #Change this so we can switch between prod and nprod with env var/input
    with open('./public_key.pub', 'rb') as f:
        key_data = f.read()
        imported_key = gpg.import_keys(key_data)
        fingerprint = imported_key.fingerprints[0]

    # Encrypt the JSON string with PGP
    encrypted_data = gpg.encrypt(json_str, recipients=fingerprint, always_trust=True)

    # Upload the encrypted data to GCP bucket
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.upload_from_string(encrypted_data)
    # add in how to get HTTP response from upload above. Check GCP's docs as to how to get response eg status: 200 vs status 400-405
    status_code = 200
    return status_code

def lambda_handler(event, context):
    for record in event['Records']:
        key = record['s3']['object']['key']
        bucket = record['s3']['bucket']['name']

        # Retrieve the JSON file from S3
        response = s3_client.get_object(Bucket=bucket, Key=key)
        file_content = response['Body'].read().decode('utf-8')
        file_json = json.loads(file_content)
        if len(file_json) > 1 and list(set(file_json[0].value())) != [None]:
             # Parse the JSON content
            upload = encrypt_and_upload_to_gcp(file_content, bucket, key)
            if upload == 200:
                response = sns_client.publish(
                    TopicArn=os.getenv('TOPIC_ARN'),
                    Message='A file with content was encrypted and uploaded to their GCP bucket'
                )
            else:
                response = sns_client.publish(
                    TopicArn=os.getenv('TOPIC_ARN'),
                    Message='A file with content was encrypted and not uploaded to their GCP bucket'
                )
        else:
            response = sns_client.publish(
                TopicArn=os.getenv('TOPIC_ARN'),
                Message='The file contained no data '
            )
