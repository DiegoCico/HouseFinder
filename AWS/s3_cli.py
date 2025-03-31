import argparse
import json
from s3_storage import S3Storage


def main():
    parser = argparse.ArgumentParser(
        description='S3 Storage CLI for managing files on S3.'
    )
    subparsers = parser.add_subparsers(dest='command', required=True)

    # List command: list all objects in the bucket.
    subparsers.add_parser('list', help='List all files in the bucket.')

    # Store command: store JSON data from a local file into S3.
    store_parser = subparsers.add_parser('store', help='Store JSON data in S3.')
    store_parser.add_argument('local_file', help='Path to local JSON file.')
    store_parser.add_argument('s3_key', help='S3 key (filename) for the JSON data.')

    # Retrieve command: retrieve JSON data from S3.
    retrieve_parser = subparsers.add_parser('retrieve', help='Retrieve JSON data from S3.')
    retrieve_parser.add_argument('s3_key', help='S3 key (filename) of the JSON data.')
    retrieve_parser.add_argument('--output', '-o', help='Local file to save the retrieved JSON. If omitted, prints to stdout.')

    # Delete command: delete an object from S3.
    delete_parser = subparsers.add_parser('delete', help='Delete an object from S3.')
    delete_parser.add_argument('s3_key', help='S3 key (filename) to delete.')

    # Upload command: upload any local file to S3.
    upload_parser = subparsers.add_parser('upload', help='Upload a file to S3.')
    upload_parser.add_argument('local_file', help='Path to local file.')
    upload_parser.add_argument('s3_key', help='S3 key (filename) for the file.')

    # Download command: download a file from S3.
    download_parser = subparsers.add_parser('download', help='Download a file from S3.')
    download_parser.add_argument('s3_key', help='S3 key (filename) to download.')
    download_parser.add_argument('local_file', help='Local filename to save the downloaded file.')

    args = parser.parse_args()
    storage = S3Storage()

    if args.command == 'list':
        storage.list_files()

    elif args.command == 'store':
        try:
            with open(args.local_file, 'r') as f:
                data = json.load(f)
            storage.store_data(data, args.s3_key)
        except Exception as e:
            print(f"Error reading file or storing data: {e}")

    elif args.command == 'retrieve':
        data = storage.retrieve_data(args.s3_key)
        if data is not None:
            if args.output:
                try:
                    with open(args.output, 'w') as f:
                        json.dump(data, f, indent=2)
                    print(f"Data saved to {args.output}")
                except Exception as e:
                    print(f"Error writing to file: {e}")
            else:
                print(json.dumps(data, indent=2))
        else:
            print("No data found or error retrieving data.")

    elif args.command == 'delete':
        storage.delete_file(args.s3_key)

    elif args.command == 'upload':
        storage.upload_file(args.local_file, args.s3_key)

    elif args.command == 'download':
        storage.download_file(args.s3_key, args.local_file)


if __name__ == '__main__':
    main()
