import boto3
import os
import sys
from tqdm import tqdm

def test_bucket_takeover(bucket_name):
    try:
        # Connect to S3
        s3 = boto3.client("s3")

        # Check if the bucket exists
        s3.head_bucket(Bucket=bucket_name)
    except boto3.client.exceptions.ClientError as e:
        if e.response['Error']['Code'] == '404':
            print(f"Error: Bucket {bucket_name} does not exist.")
            return
        else:
            print(f"Error: {e}")
            return
    try:
        # Check if the bucket is publicly accessible
        result = s3.get_bucket_acl(Bucket=bucket_name)
        if result['Grants'][0]['Grantee']['Type'] == 'Group':
            if result['Grants'][0]['Grantee']['URI'] == 'http://acs.amazonaws.com/groups/global/AllUsers':
                print(f"Bucket {bucket_name} is publicly accessible.")
                # Create a test file
                with open("test_file.txt", "w") as f:
                    f.write("test file")
                try:
                    # Try to upload a file to the bucket
                    with tqdm(unit='B', unit_scale=True, desc='Upload Progress') as pbar:
                        s3.upload_file("test_file.txt", bucket_name, "test_file.txt", Callback=lambda x: pbar.update(x))
                    print(f"\nSuccessfully uploaded test_file.txt to {bucket_name}.")
                    # Try to delete the file from the bucket
                    with tqdm(unit='B', unit_scale=True, desc='Delete Progress') as pbar:
                        s3.delete_object(Bucket=bucket_name, Key="test_file.txt")
                    print(f"\nSuccessfully deleted test_file.txt from {bucket_name}.")
                except Exception as e:
                    print(f"Error: {e}")
                    print(f"Unable to upload or delete file from bucket {bucket_name}.")
                # Remove the test file
                os.remove("test_file.txt")
            else:
                print(f"Bucket {bucket_name} is not publicly accessible.")
    except Exception as e:
        print(f"Error: {e}")
        print(f"Unable to determine if bucket {bucket_name} is publicly accessible.")

if len(sys.argv) != 2:
    print("Please provide a bucket name as an argument.")
    sys.exit()

# Test an S3 bucket
test_bucket_takeover(sys.argv[1])
