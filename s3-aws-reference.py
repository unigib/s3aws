#!/usr/bin/env python3
"""
s3_object_ops.py - S3 API & Pre-Signed URL Demonstration
Executed on EC2 using IAM Instance Profile credentials.
"""

import boto3
import requests
from botocore.exceptions import ClientError

# 1. Initialize S3 client (automatically uses EC2 metadata credentials)
s3 = boto3.client("s3")
BUCKET_NAME = "cs-cloud-storage-<your-student-id>"
OBJECT_KEY = "datasets/telemetry_2026.json"

# 2. Upload an object with User-Defined and System Metadata
payload = b'{"sensor": "temp_probe_01", "status": "active", "reading": 23.4}'
print(f"[*] Uploading object to s3://{BUCKET_NAME}/{OBJECT_KEY}...")

s3.put_object(
    Bucket=BUCKET_NAME,
    Key=OBJECT_KEY,
    Body=payload,
    ContentType="application/json",
    Metadata={
        "author": "student-admin",
        "lab-session": "lab-05",
        "datacenter-zone": "eu-west-1a"
    }
)

# 3. Inspect HeadObject (Fetches metadata without downloading the body)
print("[*] Retrieving Object Metadata via HeadObject...")
head_resp = s3.head_object(Bucket=BUCKET_NAME, Key=OBJECT_KEY)
print(f"    - Content-Type: {head_resp['ContentType']}")
print(f"    - ETag (MD5 Hash): {head_resp['ETag']}")
print(f"    - User Metadata: {head_resp['Metadata']}")

# 4. Generate a Pre-Signed URL (Delegated Read Access for 5 minutes)
# Architectural insight: The EC2 instance authorizes access without proxying the bytes.
try:
    presigned_url = s3.generate_presigned_url(
        ClientMethod="get_object",
        Params={"Bucket": BUCKET_NAME, "Key": OBJECT_KEY},
        ExpiresIn=300
    )
    print(f"\n[*] Generated Pre-Signed GET URL (Valid 300s):\n{presigned_url}\n")
    
    # 5. Simulate an external client fetching the file directly from S3
    client_fetch = requests.get(presigned_url)
    print(f"[*] External Client Verification: HTTP {client_fetch.status_code}")
    print(f"[*] Fetched Content: {client_fetch.text}")

except ClientError as e:
    print(f"Error: {e}")