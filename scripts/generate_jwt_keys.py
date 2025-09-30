#!/usr/bin/env python3
"""Generate JWT keys for development."""

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
import os

def generate_jwt_keys():
    """Generate RSA key pair for JWT signing."""
    
    # Generate private key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    
    # Get public key
    public_key = private_key.public_key()
    
    # Serialize private key
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    
    # Serialize public key
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    
    # Create secrets directory
    secrets_dir = "secrets"
    os.makedirs(secrets_dir, exist_ok=True)
    
    # Write keys to files
    with open(f"{secrets_dir}/jwt_private.pem", "wb") as f:
        f.write(private_pem)
    
    with open(f"{secrets_dir}/jwt_public.pem", "wb") as f:
        f.write(public_pem)
    
    print("JWT keys generated successfully!")
    print(f"   - Private key: {secrets_dir}/jwt_private.pem")
    print(f"   - Public key: {secrets_dir}/jwt_public.pem")

if __name__ == "__main__":
    generate_jwt_keys()
