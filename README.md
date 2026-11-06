# AWS S3 Object Storage Lab

This assignment compares AWS S3 object storage with traditional NAS/SAN storage and demonstrates how applications can use S3 metadata and time-limited pre-signed URLs to transfer files directly between a client and S3.

## Learning objectives

- Provision a private S3 bucket and keep public access blocked.
- Upload an object and inspect its system and user-defined metadata.
- Generate and test time-limited pre-signed GET and PUT URLs.
- Explain how direct S3 transfers reduce application-server bandwidth use.
- Compare object storage with NAS/SAN architectures.

## Lab portal

The interactive portal includes an architecture visualizer and a live transfer-testing studio. If you are deploying the portal as the lecturer:

1. Push this repository to GitHub.
2. In [Vercel](https://vercel.com), choose **Add New > Project** and import the repository.
3. Keep the default **Other** framework settings and deploy.
4. Share the generated Vercel URL with students, or add it to the Canvas assignment.

## Student assignment

### Prerequisites

- An AWS account and permission to create and use an S3 bucket.
- Python 3.
- AWS credentials supplied through an EC2 instance role or environment variables.
- The Vercel lab portal URL supplied by your instructor.

Use an IAM identity with only the permissions needed for this lab. Do not commit credentials or post them in the portal, screenshots, or submitted work. On EC2, prefer an attached IAM role instead of access keys.

### 1. Install the project dependencies

From the repository directory:

```bash
python -m venv .venv
```

Activate the environment and install dependencies:

```bash
# macOS/Linux
source .venv/bin/activate

# Windows PowerShell
.\.venv\Scripts\Activate.ps1

python -m pip install -r requirements.txt
```

### 2. Configure AWS and create the private bucket

Set the environment variables for your shell or configure the EC2 instance role. For example, in PowerShell:

```powershell
$env:AWS_ACCESS_KEY_ID = "your_access_key"
$env:AWS_SECRET_ACCESS_KEY = "your_secret_key"
$env:AWS_DEFAULT_REGION = "us-east-1"
$env:VAULT_BUCKET_NAME = "vault-your-student-id-lab"
```

On macOS/Linux, use `export NAME="value"` for each variable. Choose a globally unique bucket name. The scripts use `VAULT_BUCKET_NAME` for the private vault; its default value is only a placeholder.

Create the bucket, enable the script's public-access block and CORS configuration, then upload a sample image and generate temporary links:

```bash
python setup_storage.py
python generate_links.py
```

The generated GET URL is valid for 60 seconds and the PUT URL for 300 seconds. Anyone holding a pre-signed URL can use it until it expires, so treat these URLs as temporary credentials.

### 3. Test direct transfers in the portal

1. Open the Vercel lab portal and go to its live URL testing studio.
2. Paste the generated GET URL into the download test and verify the image loads directly from S3.
3. Paste the generated PUT URL into the upload test, select a PNG, and verify the direct upload succeeds.
4. Wait for the GET URL to expire, then test it again and observe the access-denied response.

### 4. Run the S3 object-operations reference script

The reference script demonstrates uploading a JSON object, inspecting it with `head_object`, and generating a pre-signed GET URL. It uses the credentials available to the process, including an EC2 instance role when run on EC2.

Before running it, edit `BUCKET_NAME` in `s3-aws-reference.py` to the bucket you created. Then run:

```bash
python s3-aws-reference.py
```

The script uploads `datasets/telemetry_2026.json`, prints the content type, ETag, and user metadata, then fetches the object using a pre-signed GET URL that is valid for 300 seconds. Do not share the printed URL publicly.

### 5. Submit

Submit the following through Canvas:

1. A screenshot showing your S3 bucket with **Block all public access** enabled and the CORS configuration saved.
2. A screenshot of the portal showing a successful direct download and direct upload.
3. A screenshot showing the expired GET link returning an access-denied response.
4. One paragraph explaining how direct S3 transfers reduce application-server bandwidth use compared with serving files from a mounted NAS directory.

## Troubleshooting

- **AccessDenied or NoCredentialsError:** Check the active AWS credentials or EC2 role and ensure it has the required bucket permissions.
- **NoSuchBucket:** Check the bucket name and region.
- **SignatureDoesNotMatch:** Make sure the URL was copied in full and the system clock is synchronized.
- **Expired URL:** Generate a new link; pre-signed URLs work only for their configured time limit.
