import time 
import busio
import board
from adafruit_pn532.i2c import PN532_I2C
from digitalio import DigitalInOut
import adafruit_pn532.adafruit_pn532 as nfc
import hashlib
from Crypto.Hash import SHA256
from Crypto.Signature import PKCS1_v1_5
from Crypto.PublicKey import RSA

# Hardware setup (exact same as writer)
reset_pin = DigitalInOut(board.D23)
req_pin = DigitalInOut(board.D24)
i2c = busio.I2C(board.SCL, board.SDA)
pn532 = PN532_I2C(i2c, debug=False, reset=reset_pin, req=req_pin)
pn532.SAM_configuration()

key_a = b"\xFF\xFF\xFF\xFF\xFF\xFF"
non_writable_block_list = [0,3,7,11,15,19,23,27,31,35,39,43,47,51,55,59,63]

def read_block_func(block_index):
    """Read single block - exact match to writer blocks"""
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

# EXACT SAME BLOCK INDICES as your writer (12 data + 4 signature)
data_block_indices = [1,2,4,5,6,8,9,10,12,16,17,18]
signature_block_indices = [40,41,42,44]  # 4 blocks = 64 bytes

uid = pn532.read_passive_target(timeout=5.0)

if uid:
    print("✅ Tag found! UID =", [hex(i) for i in uid])
    uid_bytes = bytes(uid)
    
    # STEP 1: Read all data blocks (EXACT same order as writer)
    print("\n📖 Reading data blocks...")
    data_blocks = []
    for block_idx in data_block_indices:
        block_data = read_block_func(block_idx)
        if block_data:
            print(f"  Block {block_idx}: {block_data.hex()[:32]}...")
            data_blocks.append(block_data)
        else:
            print("❌ Failed to read data blocks!")
            exit(1)
    
    # STEP 2: Read signature blocks (4 blocks = 64 bytes)
    print("\n🔑 Reading signature blocks...")
    sig_blocks = []
    for block_idx in signature_block_indices:
        block_data = read_block_func(block_idx)
        if block_data:
            print(f"  Block {block_idx}: {block_data.hex()}")
            sig_blocks.append(block_data)
        else:
            print("❌ Failed to read signature!")
            exit(1)
    
    # STEP 3: Rebuild data EXACTLY like writer
    data = uid_bytes + b''.join(data_blocks)
    print(f"\n📊 Rebuilt data length: {len(data)} bytes")
    
    # STEP 4: Boss's EXACT hash method
    digest = SHA256.new()
    digest.update(data)
    print(f"📊 Data hash: {digest.hexdigest()}")
    
    # STEP 5: Rebuild signature (EXACTLY 64 bytes)
    signature = b''.join(sig_blocks)
    print(f"🔒 Read signature: {len(signature)} bytes")
    print(f"🔒 Signature hex: {signature.hex()}")
    
    # STEP 6: Load public key (Boss's method)
    try:
        with open("public_key.pem", "r") as f:
            public_key = RSA.importKey(f.read())
        print("✅ Public key loaded")
    except FileNotFoundError:
        print("❌ public_key.pem not found!")
        exit(1)
    
    # STEP 7: Boss's EXACT verification
    print("\n🔍 Verifying with Boss's RSA method...")
    verifier = PKCS1_v1_5.new(public_key)
    try:
        verified = verifier.verify(digest, signature)
        if verified:
            print("🎉 ✅ VERIFICATION PASSED!")
            print("   ➤ Battery data is AUTHENTIC!")
            print("   ➤ Signed by trusted private key!")
            
            # Show battery info from Block 1
            block1 = data_blocks[0]
            data_ver = int.from_bytes(block1[0:2], 'big')
            batt_volt_max = int.from_bytes(block1[2:5], 'big') / 100
            print(f"   🔋 Data version: {data_ver}")
            print(f"   🔋 Max voltage: {batt_volt_max}V")
        else:
            print("❌ VERIFICATION FAILED!")
            print("   ➤ Signature invalid!")
    except Exception as e:
        print("❌ VERIFICATION FAILED!")
        print(f"   ➤ Error: {e}")

else:
    print("❌ No NFC tag found!")
