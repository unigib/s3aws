# Native Cloud Object Storage: Programmatic S3 & Pre-Signed Access

This repository contains a small Python reference for working with Amazon S3 from an EC2 instance using the instance's IAM role.

The script in this repo demonstrates:

- uploading an object to S3
- reading object metadata with `head_object`
- generating a temporary pre-signed URL for delegated read access

The project is the GitHub repository `unigib/s3aws`, and the main script is `s3-aws-reference.py`.

## Repository contents

```text
.
├── README.md               # Project overview and usage notes
└── s3-aws-reference.py     # Reference script for S3 upload + metadata + pre-signed URL
```

## Prerequisites

Before running the script, make sure you have:

- an AWS EC2 instance
- an IAM role or instance profile attached to the instance with S3 permissions
- Python 3 installed
- the `boto3` and `requests` packages installed

## Setup

From a terminal on the EC2 instance:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install boto3 requests
```

If you are on Windows PowerShell, use:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install boto3 requests
```

## Configuration

Before running the script, create the target S3 bucket in AWS. The bucket must already exist before the code calls `put_object`.

You can create it with the AWS CLI:

```bash
aws s3 mb s3://your-bucket-name --region us-east-1
```

Or create it in the AWS Management Console:

1. Open **Amazon S3** in the AWS Console and choose **Create bucket**.
2. Enter a globally unique bucket name and select the AWS Region.
3. Keep the recommended settings unless your lab instructions require different settings, then choose **Create bucket**.

Then edit the `BUCKET_NAME` and `OBJECT_KEY` values at the top of `s3-aws-reference.py`:

```python
BUCKET_NAME = "your-bucket-name"
OBJECT_KEY = "datasets/telemetry_2026.json"
```

> The bucket name must be globally unique across AWS. Make sure your AWS SDK/CLI region configuration is appropriate for the bucket's region.

## Before you run

- [ ] An AWS account is available, and you can access the target EC2 instance.
- [ ] The S3 bucket has been created, using either the AWS CLI or the AWS Console.
- [ ] `BUCKET_NAME` in `s3-aws-reference.py` matches the bucket you created.
- [ ] The EC2 instance has an IAM role attached with permission to upload and read objects in that bucket (including `s3:PutObject` and `s3:GetObject`).
- [ ] Python 3 is available, and `boto3` and `requests` are installed in the active environment.
- [ ] AWS credentials are provided by the instance role; no access keys are hardcoded in the script.

## Run the script

```bash
python s3-aws-reference.py
```

This will upload a sample JSON object, print the object metadata from `head_object`, and generate a pre-signed URL for direct access.

## Notes

- Do not hardcode AWS access keys in the script.
- The code expects to use credentials that are automatically available to the EC2 instance via its IAM role.
- The pre-signed URL is time-limited and is intended for short-lived delegated access.

## Typical troubleshooting

- `AccessDenied` or `NoCredentialsError`: check that the EC2 instance has the correct IAM role attached.
- `NoSuchBucket`: confirm the bucket name and region are correct.
- `SignatureDoesNotMatch`: verify the URL is not truncated and that the instance clock is reasonably in sync.

## What to expect from the pre-signed URL

The script generates a pre-signed **GET** URL that grants temporary read access to the uploaded object. It is valid for 300 seconds (5 minutes). Anyone with the URL can use it during that period, without AWS credentials, so treat it like a temporary password and do not post or share it publicly.

While it is valid, opening the URL in a browser or requesting it with `curl` should return HTTP `200` and the uploaded JSON:

```json
{"sensor": "temp_probe_01", "status": "active", "reading": 23.4}
```

For example, copy the URL printed by the script and run:

```bash
curl -i "<PASTE_PRESIGNED_URL_HERE>"
```

After the 5-minute expiration window, the same request should fail with HTTP `403 Forbidden` and an S3 error indicating that the request has expired. The script also tests the URL immediately and prints the HTTP status and returned content.
