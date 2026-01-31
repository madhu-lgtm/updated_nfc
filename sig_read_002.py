#Working
import time 
import busio
import board
from adafruit_pn532.i2c import PN532_I2C
from digitalio import DigitalInOut
import adafruit_pn532.adafruit_pn532 as nfc
from Crypto.Hash import SHA256
from Crypto.Signature import PKCS1_v1_5
from Crypto.PublicKey import RSA

reset_pin = DigitalInOut(board.D23)
req_pin = DigitalInOut(board.D24)
i2c = busio.I2C(board.SCL, board.SDA)
pn532 = PN532_I2C(i2c, debug=False, reset=reset_pin, req=req_pin)
pn532.SAM_configuration()

key_a = b"\xFF\xFF\xFF\xFF\xFF\xFF"

def read_block_func(block_index):
    if pn532.mifare_classic_authenticate_block(uid, block_index, nfc.MIFARE_CMD_AUTH_A, key_a):
        block_data = pn532.mifare_classic_read_block(block_index)
        if block_data:
            return bytes(block_data)
    print(f"Read failed: Block {block_index}")
    return None

# SAME BLOCKS as writer (12 data + 8 signature)
data_block_indices = [1,2,4,5,6,8,9,10,12,16,17,18]
signature_block_indices = [40,41,42,44,45,46,48,49]  # 8 blocks = 128 bytes

uid = pn532.read_passive_target(timeout=5.0)

if uid:
    print("Tag found! UID =", [hex(i) for i in uid])
    uid_bytes = bytes(uid)
    
    # Read data blocks
    print("\nReading data blocks...")
    data_blocks = []
    for block_idx in data_block_indices:
        block_data = read_block_func(block_idx)
        if block_data:
            print(f"  Block {block_idx}: {block_data.hex()[:24]}...")
            data_blocks.append(block_data)
        else:
            print("Data read failed!")
            exit(1)
    
    # Read signature blocks (8 blocks = 128 bytes)
    print("\nReading signature blocks...")
    sig_blocks = []
    for block_idx in signature_block_indices:
        block_data = read_block_func(block_idx)
        if block_data:
            print(f"  Block {block_idx}: {block_data.hex()}")
            sig_blocks.append(block_data)
        else:
            print("Signature read failed!")
            exit(1)
    
    # Rebuild EXACT data
    data = uid_bytes + b''.join(data_blocks)
    print(f"\nData length: {len(data)} bytes")
    
    # Boss's EXACT hash method
    digest = SHA256.new()
    digest.update(data)
    print(f"Data hash: {digest.hexdigest()}")
    
    # Rebuild FULL 128-byte signature
    signature = b''.join(sig_blocks)
    print(f"Full signature: {len(signature)} bytes")
    
    # Load public key (Boss's method)
    with open("public_key.pem", "r") as f:
        public_key = RSA.importKey(f.read())
    print("Public key loaded")
    
    # Boss's EXACT verification
    print("\nRSA verification...")
    verifier = PKCS1_v1_5.new(public_key)
    try:
        verified = verifier.verify(digest, signature)
        if verified:
            print("VERIFICATION PASSED!")
            print("Battery data AUTHENTIC!")
            
            # Battery info
            block1 = data_blocks[0]
            data_ver = int.from_bytes(block1[0:2], 'big')
            batt_volt_max = int.from_bytes(block1[4:7], 'big')
            print(block1)
            print(f"Version: {data_ver}")
            print(f"Max voltage: {batt_volt_max} mV")
        else:
            print("Signature invalid!")
    except Exception as e:
        print("Verification error!")
        print(f"Error: {e}")

else:
    print("No tag!")
