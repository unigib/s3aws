# Lab 05: Programmatic AWS S3 Operations & Delegated Access

This repository contains the starter code and reference scripts for **CSS61501 (Cloud Computing): Lab 05**.

You will use Python (`boto3`) on an AWS EC2 instance to interact natively with Amazon S3 as an object store—bypassing traditional file-system abstractions to upload data, inspect custom metadata with `HeadObject`, and delegate secure, temporary client access using cryptographic **Pre-Signed URLs**.

---

## Architecture Overview

```text
                      ┌────────────────────────────────────────┐
                      │              AWS Cloud                 │
                      │                                        │
                      │   ┌──────────────┐                     │
                      │   │  IAM Role    │                     │
                      │   └──────┬───────┘                     │
                      │          │ (Auto-injected STS tokens)  │
                      │          ▼                             │
┌──────────────┐      │   ┌──────────────┐                     │
│ External     │      │   │ EC2 Instance │                     │
│ Client /     │      │   │ (Compute)    │                     │
│ Browser      │      │   └──────┬───────┘                     │
└──────┬───────┘      │          │                             │
       │              │          │ 1. put_object (with meta)   │
       │              │          │ 2. head_object              │
       │              │          │ 3. generate_presigned_url   │
       │              │          ▼                             │
       │              │   ┌──────────────────────────────┐     │
       │ 4. Direct    │   │ Amazon S3 Bucket             │     │
       │    HTTP GET/ │   │ (Object Storage)             │     │
       └──────────────┴──►│                              │     │
            PUT           └──────────────────────────────┘     │
                                                               │
───────────────────────────────────────────────────────────────┘
```

---

## Prerequisites

Before running the script, ensure you have:

1. An active **Ubuntu 24.04 EC2 instance** running.
2. An **IAM Instance Profile (Role)** attached to your EC2 instance that allows S3 read/write actions (e.g., `AmazonS3FullAccess` or scoped bucket permissions).
   > **Important:** Do **not** hardcode AWS access keys (`aws_access_key_id` or `aws_secret_access_key`) inside the script. `boto3` automatically retrieves rotating credentials from the EC2 Instance Metadata Service (IMDS).
3. Python 3.10+ installed on your instance.

---

## Setup & Installation

SSH into your EC2 instance and run the following commands to clone the repository and set up an isolated virtual environment:

```bash
# 1. Clone the repository
git clone https://github.com/<your-org-or-username>/lab05-s3-operations.git
cd lab05-s3-operations

# 2. Update package lists and install python venv
sudo apt update && sudo apt install -y python3-pip python3-venv

# 3. Create and activate a Python virtual environment
python3 -m venv venv
source venv/bin/activate

# 4. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

> **Note:** Whenever you reconnect to your EC2 instance, remember to re-activate the virtual environment:
> ```bash
> source venv/bin/activate
> ```

---

## Configuration

Open `s3_object_ops.py` in your text editor (such as `nano` or `vim`):

```bash
nano s3_object_ops.py
```

Set your unique bucket name at the top of the script:

```python
# Replace with your actual student S3 bucket name
BUCKET_NAME = "cs-cloud-storage-<your-student-id>"
OBJECT_KEY = "datasets/telemetry_2026.json"
```

> **Reminder:** S3 bucket names are globally unique across all AWS accounts. If you haven't created your bucket yet, you can create one using the AWS CLI:
> ```bash
> aws s3 mb s3://cs-cloud-storage-<your-student-id> --region <your-region>
> ```

---

## Running the Script

Execute the script inside your virtual environment:

```bash
python s3_object_ops.py
```

### Expected Output

```text
[*] Initializing S3 client via EC2 Instance Profile...
[*] Uploading object to s3://cs-cloud-storage-12345/datasets/telemetry_2026.json...
[+] Object successfully uploaded.

[*] Retrieving Object Metadata via HeadObject...
    - Content-Type : application/json
    - ETag         : "b10a8db164e0754105b7a99be72e3fe5"
    - Last-Modified: Wed, 04 Nov 2026 16:20:00 GMT
    - User Metadata: {'author': 'student-admin', 'lab-session': 'lab-05', 'datacenter-zone': 'eu-west-1a'}

[*] Generating Pre-Signed GET URL (Valid for 300 seconds)...
[+] URL: https://cs-cloud-storage-12345.s3.amazonaws.com/datasets/telemetry_2026.json?AWSAccessKeyId=...

[*] Testing external client fetch via generated Pre-Signed URL...
    - HTTP Status  : 200 OK
    - Body Received: {"sensor": "temp_probe_01", "status": "active", "reading": 23.4}
```

---

## Verification & Experiments

### 1. Verify via AWS CLI
From your terminal, verify that the object exists in your bucket:

```bash
aws s3 ls s3://<your-bucket-name>/datasets/
```

### 2. Verify with `curl` from a Local Machine
Copy the Pre-Signed URL printed in your terminal and test it from your **local machine** (outside AWS):

```bash
curl -i "<PASTE_PRESIGNED_URL_HERE>"
```
You should receive an `HTTP/1.1 200 OK` response along with the JSON body without providing any AWS credentials.

### 3. Test Expiration
Wait for the expiration window to pass (default: 300 seconds) and run the `curl` command again:

```bash
curl -i "<PASTE_PRESIGNED_URL_HERE>"
```
You should now receive an `HTTP/1.1 403 Forbidden` response containing an XML error indicating `Request has expired`.

---

## Troubleshooting

| Error | Cause | Resolution |
| :--- | :--- | :--- |
| `NoCredentialsError` / `ClientError: AccessDenied` | IAM role is not attached to the instance or lacks S3 policies. | Go to AWS Console &rarr; EC2 &rarr; Select Instance &rarr; **Actions &rarr; Security &rarr; Modify IAM role**. |
| `NoSuchBucket` | The bucket defined in `BUCKET_NAME` does not exist. | Create the bucket using `aws s3 mb s3://<your-bucket-name>`. |
| `SignatureDoesNotMatch` | The pre-signed URL was truncated, corrupted, or the system clock on EC2 is out of sync. | Ensure you enclose the URL in double quotes (`"..."`) when passing it to `curl`. Run `timedatectl` to verify NTP sync. |

---

## Repository Structure

```text
.
├── README.md              # Setup and execution guide
├── requirements.txt       # Python dependencies (boto3, requests)
└── s3_object_ops.py       # Main script: S3 API, metadata, and pre-signed URLs
```