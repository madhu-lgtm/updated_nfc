import time, busio, board, hashlib
from adafruit_pn532.i2c import PN532_I2C
from digitalio import DigitalInOut
import adafruit_pn532.adafruit_pn532 as nfc
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec

# Hardware (same)
reset_pin = DigitalInOut(board.D23)
req_pin = DigitalInOut(board.D24)
i2c = busio.I2C(board.SCL, board.SDA)
pn532 = PN532_I2C(i2c, debug=False, reset=reset_pin, req=req_pin)
pn532.SAM_configuration()

key_a = b"\xFF\xFF\xFF\xFF\xFF\xFF"

def read_block(idx):
    if pn532.mifare_classic_authenticate_block(uid, idx, nfc.MIFARE_CMD_AUTH_A, key_a):
        data = pn532.mifare_classic_read_block(idx)
        return bytes(data) if data else None
    return None

data_indices = [1,2,4,5,6,8,9,10,12,16,17,18]
sig_indices = [40,41,42,44]

uid = pn532.read_passive_target(timeout=5.0)
if uid:
    print("🎯 Tag found!")
    
    # Read blocks
    data_blocks = [read_block(i) for i in data_indices]
    sig_blocks = [read_block(i) for i in sig_indices]
    
    if all(data_blocks) and all(sig_blocks):
        # Rebuild data + checksum
        data = bytes(uid) + b''.join(data_blocks)
        checksum = hashlib.sha256(data).digest()
        
        # Rebuild signature (EXACTLY 64 bytes)
        signature = b''.join(sig_blocks)
        print(f"Got signature: {len(signature)} bytes")
        
        # Verify
        with open("public_key.pem", "rb") as f:
            pub_key = serialization.load_pem_public_key(f.read())
        
        try:
            pub_key.verify(signature, checksum, ec.ECDSA(hashes.SHA256()))
            print("🎉 ✅ VERIFIED!")
            print("   Data is authentic!")
        except:
            print("❌ FAILED!")
            print(f"Checksum: {checksum.hex()}")
            print(f"Signature: {signature.hex()}")
    else:
        print("❌ Read failed!")
else:
    print("❌ No tag!")
