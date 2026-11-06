import os
import boto3

VAULT_BUCKET = os.getenv("VAULT_BUCKET_NAME", "my-s3-vault-lab-xyz")
REGION = os.getenv("AWS_REGION", "us-east-1")

s3 = boto3.client('s3', region_name=REGION)

def setup_vault():
    print(f"Creating Private Media Vault: {VAULT_BUCKET}...")
    if REGION == "us-east-1":
        s3.create_bucket(Bucket=VAULT_BUCKET)
    else:
        s3.create_bucket(
            Bucket=VAULT_BUCKET,
            CreateBucketConfiguration={'LocationConstraint': REGION}
        )

    # Block 100% of public access (Vault security pattern)
    s3.put_public_access_block(
        Bucket=VAULT_BUCKET,
        PublicAccessBlockConfiguration={
            'BlockPublicAcls': True,
            'IgnorePublicAcls': True,
            'BlockPublicPolicy': True,
            'RestrictPublicBuckets': True
        }
    )
    print("✓ Public access blocked.")

    # Configure CORS so web browsers on Vercel can stream directly
    cors_config = {
        'CORSRules': [{
            'AllowedHeaders': ['*'],
            'AllowedMethods': ['GET', 'PUT', 'HEAD'],
            'AllowedOrigins': ['*'],
            'ExposeHeaders': ['ETag'],
            'MaxAgeSeconds': 3000
        }]
    }
    s3.put_bucket_cors(Bucket=VAULT_BUCKET, CORSConfiguration=cors_config)
    print("✓ Bucket CORS enabled.")

if __name__ == "__main__":
    setup_vault()
