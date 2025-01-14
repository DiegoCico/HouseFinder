import boto3
import configparser
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

config = configparser.ConfigParser()
config.read('secrets.config')

BUCKET_NAME = config.get('aws', 'bucket_name', fallback=None)
AWS_REGION = config.get('aws', 'region', fallback='us-east-1')

if not BUCKET_NAME:
    raise ValueError("Bucket name not found in secrets.config")

# Initialize S3 Client
def initialize_s3_client():
    try:
        s3 = boto3.client('s3', region_name=AWS_REGION)
        print(f"Connected to S3 bucket '{BUCKET_NAME}' successfully!")
        return s3
    except PartialCredentialsError:
        print("Error: Partial credentials found. Please check your AWS credentials.")
    except NoCredentialsError:
        print("Error: No AWS credentials found. Please configure them.")

# List all files in the bucket
def list_files(s3):
    try:
        response = s3.list_objects_v2(Bucket=BUCKET_NAME)
        if 'Contents' in response:
            print("Files in bucket:")
            for obj in response['Contents']:
                print(f"- {obj['Key']}")
        else:
            print("Bucket is empty.")
    except Exception as e:
        print(f"Error listing files: {e}")

# Upload a file to the bucket
def upload_file(s3, file_name, key):
    try:
        s3.upload_file(file_name, BUCKET_NAME, key)
        print(f"File '{file_name}' uploaded to '{key}' successfully!")
    except Exception as e:
        print(f"Error uploading file: {e}")

# Download a file from the bucket
def download_file(s3, key, file_name):
    try:
        s3.download_file(BUCKET_NAME, key, file_name)
        print(f"File '{key}' downloaded as '{file_name}' successfully!")source venv/bin/activate

    except Exception as e:
        print(f"Error downloading file: {e}")

# Delete a file from the bucket
def delete_file(s3, key):
    try:
        s3.delete_object(Bucket=BUCKET_NAME, Key=key)
        print(f"File '{key}' deleted successfully!")
    except Exception as e:
        print(f"Error deleting file: {e}")

# Main function to test functionality
if __name__ == "__main__":
    # Initialize S3 client
    s3_client = initialize_s3_client()
    if s3_client:
        # Test listing files
        list_files(s3_client)

        # Test uploading a file
        # Replace 'local_file.txt' with a file on your local system
        upload_file(s3_client, 'local_file.txt', 'uploaded_file.txt')

        # Test downloading a file
        download_file(s3_client, 'uploaded_file.txt', 'downloaded_file.txt')

        # Test deleting a file
        delete_file(s3_client, 'uploaded_file.txt')
