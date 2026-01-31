import time 
import busio
import board
from adafruit_pn532.i2c import PN532_I2C
from digitalio import DigitalInOut
import adafruit_pn532.adafruit_pn532 as nfc
import hashlib
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec

# Same hardware setup
reset_pin = DigitalInOut(board.D23)
req_pin = DigitalInOut(board.D24)
i2c = busio.I2C(board.SCL, board.SDA)
pn532 = PN532_I2C(i2c, debug=False, reset=reset_pin, req=req_pin)
pn532.SAM_configuration()

key_a = b"\xFF\xFF\xFF\xFF\xFF\xFF"

def read_block_func(block_index):
    """Read a single block from NFC tag"""
    if pn532.mifare_classic_authenticate_block(uid, block_index, nfc.MIFARE_CMD_AUTH_A, key_a):
        block_data = pn532.mifare_classic_read_block(block_index)
        if block_data:
            return bytes(block_data)
        else:
            print(f"Failed to read block {block_index}")
            return None
    else:
        print(f"Failed to authenticate block {block_index}")
        return None

# Block indices that contain data (same as writer)
data_block_indices = [1,2,4,5,6,8,9,10,12,16,17,18]
signature_block_indices = [40,41,42,44,45]  # 5 blocks = 80 bytes total

uid = pn532.read_passive_target(timeout=5.0)

if uid:
    print("✅ Tag found! UID =", [hex(i) for i in uid])
    uid_bytes = bytes(uid)
    
    # STEP 1: Read all data blocks
    print("\n📖 Reading data blocks...")
    data_blocks = []
    for block_idx in data_block_indices:
        block_data = read_block_func(block_idx)
        if block_data:
            print(f"  Block {block_idx}: {block_data}")
            data_blocks.append(block_data)
        else:
            print("❌ Failed to read all data blocks!")
            exit(1)
    
    # STEP 2: Read signature blocks (5 blocks = 80 bytes)
    print("\n🔑 Reading signature blocks...")
    sig_blocks = []
    for block_idx in signature_block_indices:
        block_data = read_block_func(block_idx)
        if block_data:
            print(f"  Block {block_idx}: {block_data}")
            sig_blocks.append(block_data)
        else:
            print("❌ Failed to read signature!")
            exit(1)
    
    # STEP 3: Rebuild data and checksum (exactly like writer)
    data = uid_bytes + b''.join(data_blocks)
    checksum = hashlib.sha256(data).digest()
    print(f"\n📊 Recomputed checksum: {checksum.hex()}")
    
    # STEP 4: Rebuild FULL signature from 5 blocks (up to 72 bytes)
    full_signature_raw = b''.join(sig_blocks)  # 80 bytes from 5 blocks
    signature = full_signature_raw[:72]  # Take first 72 bytes (typical ECDSA length)
    print(f"🔒 Full signature read: {len(full_signature_raw)} bytes")
    print(f"🔒 Using signature: {len(signature)} bytes")
    print(f"🔒 Signature hex: {signature.hex()}")
    
    # STEP 5: Load PUBLIC key (shared with readers)
    try:
        with open("public_key.pem", "rb") as f:
            public_key = serialization.load_pem_public_key(f.read())
        print("✅ Public key loaded")
    except FileNotFoundError:
        print("❌ public_key.pem not found! Generate it first.")
        exit(1)
    
    # STEP 6: VERIFY full signature
    print("\n🔍 Verifying FULL signature...")
    try:
        public_key.verify(signature, checksum, ec.ECDSA(hashes.SHA256()))
        print("🎉 ✅ VERIFICATION PASSED!")
        print("   ➤ Battery data is AUTHENTIC and UNMODIFIED!")
        print("   ➤ Signed by trusted private key holder!")
        
        # Bonus: Display some battery info
        block1 = data_blocks[0]
        data_ver = int.from_bytes(block1[0:2], 'big')
        batt_volt_max = int.from_bytes(block1[2:5], 'big')
        print(f"   Battery data version: {data_ver}")
        print(f"   Max voltage: {batt_volt_max/100}V")
        
    except Exception as e:
        print("❌ VERIFICATION FAILED!")
        print(f"   ➤ Data has been TAMPERED WITH or wrong key!")
        print(f"   Error: {e}")

else:
    print("❌ No NFC tag found!")
