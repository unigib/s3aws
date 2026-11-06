import os
import boto3

VAULT_BUCKET = os.getenv("VAULT_BUCKET_NAME", "my-s3-vault-lab-xyz")
s3 = boto3.client('s3')

SAMPLE_KEY = "vault/confidential-diagram.png"

def seed_sample_asset():
    # 1x1 transparent PNG binary bytes
    tiny_png = (
        b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01'
        b'\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\rIDATx\x9cc`\x00\x00\x00'
        b'\x02\x00\x01H\xaf\xa4q\x00\x00\x00\x00IEND\xaeB`\x82'
    )
    s3.put_object(
        Bucket=VAULT_BUCKET,
        Key=SAMPLE_KEY,
        Body=tiny_png,
        ContentType="image/png"
    )
    print(f"✓ Seeded test image: s3://{VAULT_BUCKET}/{SAMPLE_KEY}")

def generate_urls():
    # Ephemeral GET URL (Valid 60 seconds)
    get_url = s3.generate_presigned_url(
        ClientMethod='get_object',
        Params={'Bucket': VAULT_BUCKET, 'Key': SAMPLE_KEY},
        ExpiresIn=60
    )

    # Ephemeral PUT URL (Valid 300 seconds)
    put_url = s3.generate_presigned_url(
        ClientMethod='put_object',
        Params={
            'Bucket': VAULT_BUCKET,
            'Key': 'vault/direct-user-upload.png',
            'ContentType': 'image/png'
        },
        ExpiresIn=300
    )

    print("\n=== PASTE THESE INTO YOUR VERCEL APP ===")
    print(f"\nPresigned GET URL (Valid 60s):\n{get_url}")
    print(f"\nPresigned PUT URL (Valid 300s):\n{put_url}\n")

if __name__ == "__main__":
    seed_sample_asset()
    generate_urls()
