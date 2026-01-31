import hashlib
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.ec import EllipticCurvePrivateKey

# STEP 1: Generate key pair (do this ONCE, save to files)
private_key = ec.generate_private_key(ec.SECP256R1())  # Common curve
public_key = private_key.public_key()

# Save private key (KEEP SECRET!)
with open("private_key.pem", "wb") as f:
    f.write(private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ))

# Save public key (share with readers)
with open("public_key.pem", "wb") as f:
    f.write(public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ))

print("✅ Keys generated! private_key.pem = secret, public_key.pem = share")

# STEP 2: Your NFC data (same as your code)
uid_bytes = b'\x04\x8a\x9c\x1f\x80'  # example UID
data = uid_bytes + b'your_block_data_here...'  # your concatenated blocks
checksum = hashlib.sha256(data).digest()
print(f"checksum: {checksum.hex()}")

# STEP 3: SIGN with private key (in your NFC writer)
signature = private_key.sign(checksum, ec.ECDSA(hashes.SHA256()))
print(f"signature (72 bytes): {signature.hex()}")

# STEP 4: VERIFY with public key (in NFC readers)
try:
    public_key.verify(signature, checksum, ec.ECDSA(hashes.SHA256()))
    print("✅ Signature VALID - data is authentic!")
except:
    print("❌ Signature INVALID - data tampered!")

# STEP 5: For NFC - split signature into 16-byte blocks
sig_blocks = [signature[i:i+16] for i in range(0, len(signature), 16)]
print(f"NFC blocks: {[b.hex() for b in sig_blocks]}")
