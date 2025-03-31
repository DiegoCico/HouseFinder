import boto3
import configparser
import json
from botocore.exceptions import NoCredentialsError, PartialCredentialsError


class S3Storage:
    """
    Handles storage operations (add, retrieve, list, delete) in an S3 bucket.
    Data is stored as JSON (when using store_data and retrieve_data) but you can also
    use upload_file and download_file for any file type.
    """

    def __init__(self, config_file='secrets.config'):
        self.config = configparser.ConfigParser()
        self.config.read(config_file)
        self.bucket_name = self.config.get('aws', 'bucket_name', fallback=None)
        self.region = self.config.get('aws', 'region', fallback='us-east-1')
        if not self.bucket_name:
            raise ValueError("Bucket name not found in secrets.config")
        self.s3 = self.initialize_s3_client()

    def initialize_s3_client(self):
        """Initializes the S3 client."""
        try:
            s3 = boto3.client('s3', region_name=self.region)
            print(f"Connected to S3 bucket '{self.bucket_name}' successfully!")
            return s3
        except PartialCredentialsError:
            raise Exception("Error: Partial credentials found. Please check your AWS credentials.")
        except NoCredentialsError:
            raise Exception("Error: No AWS credentials found. Please configure them.")

    def list_files(self):
        """Lists all files in the bucket."""
        try:
            response = self.s3.list_objects_v2(Bucket=self.bucket_name)
            if 'Contents' in response:
                files = [obj['Key'] for obj in response['Contents']]
                print("Files in bucket:")
                for file in files:
                    print(f"- {file}")
                return files
            else:
                print("Bucket is empty.")
                return []
        except Exception as e:
            print(f"Error listing files: {e}")
            return []

    def upload_file(self, file_name, key):
        """
        Uploads a local file to S3.
        
        :param file_name: The path to the local file.
        :param key: The destination filename/key in S3.
        """
        try:
            self.s3.upload_file(file_name, self.bucket_name, key)
            print(f"File '{file_name}' uploaded to '{key}' successfully!")
        except Exception as e:
            print(f"Error uploading file: {e}")

    def download_file(self, key, file_name):
        """
        Downloads a file from S3.
        
        :param key: The filename/key in S3.
        :param file_name: The path to save the file locally.
        """
        try:
            self.s3.download_file(self.bucket_name, key, file_name)
            print(f"File '{key}' downloaded as '{file_name}' successfully!")
        except Exception as e:
            print(f"Error downloading file: {e}")

    def delete_file(self, key):
        """
        Deletes a file from the S3 bucket.
        
        :param key: The filename/key in S3.
        """
        try:
            self.s3.delete_object(Bucket=self.bucket_name, Key=key)
            print(f"File '{key}' deleted successfully!")
        except Exception as e:
            print(f"Error deleting file: {e}")

    def store_data(self, data, key):
        """
        Stores a Python dictionary as a JSON file on S3.
        
        :param data: Python dictionary to store.
        :param key: The S3 key (filename) to store the JSON data, e.g. 'property_info.json'
        """
        try:
            json_data = json.dumps(data, indent=2)
            self.s3.put_object(Body=json_data, Bucket=self.bucket_name, Key=key)
            print(f"Data stored in '{key}' successfully!")
        except Exception as e:
            print(f"Error storing data: {e}")

    def retrieve_data(self, key):
        """
        Retrieves a JSON file from S3 and returns its content as a Python dictionary.
        
        :param key: The S3 key (filename) of the JSON data.
        :return: Dictionary with the stored data or None if retrieval fails.
        """
        try:
            response = self.s3.get_object(Bucket=self.bucket_name, Key=key)
            data = response['Body'].read().decode('utf-8')
            return json.loads(data)
        except Exception as e:
            print(f"Error retrieving data: {e}")
            return None
