import time 
import busio
import board
from adafruit_pn532.i2c import PN532_I2C
from digitalio import DigitalInOut
import adafruit_pn532.adafruit_pn532 as nfc
import hashlib #for checksum
from Crypto.Hash import SHA256
from Crypto.Signature import PKCS1_v1_5
from Crypto.PublicKey import RSA

reset_pin = DigitalInOut(board.D23)
req_pin = DigitalInOut(board.D24)

i2c = busio.I2C(board.SCL,board.SDA)
pn532 = PN532_I2C(i2c, debug = False, reset = reset_pin, req = req_pin)
pn532.SAM_configuration()

uid = pn532.read_passive_target(timeout=0.5)
key_a = b"\xFF\xFF\xFF\xFF\xFF\xFF"
non_writable_block_list = [0,3,7,11,15,19,23,27,31,35,39,43,47,51,55,59,63]

def write_block_func(block_index,block_contents):
    if block_index not in non_writable_block_list:      
        if pn532.mifare_classic_authenticate_block(uid,block_index,nfc.MIFARE_CMD_AUTH_A,key_a):
            if pn532.mifare_classic_write_block(block_index,block_contents):
                print("Write Ok")
            else:
                print("Write fail")    
        else:
            print("Failed to authenticate")            
    else:
        print(f"block {block_index} is Not Writable")

def convert_data_to_writable_16_bytes(*field_sizes, **fields) -> bytes:
    bytes_in_one_block = 16
    if len(field_sizes) != len(fields):
        raise ValueError("Number of field sizes must match number of keyword fields")
    total_size = sum(field_sizes)
    if total_size > bytes_in_one_block:
        raise ValueError(f"Total field bytes {total_size} exceed 16")
    result = b""
    for (name, value), size in zip(fields.items(), field_sizes):
        if isinstance(value, int):
            max_val = (1 << (8 * size)) - 1
            if not (0 <= value <= max_val):
                raise ValueError(f"Field '{name}' value {value} does not fit in {size} bytes")
            part = value.to_bytes(size, byteorder="big")
        elif isinstance(value, str):
            raw = value.encode("utf-8")[:size]
            part = raw + b"\x00" * (size - len(raw))
        else:
            raise TypeError(f"Unsupported type for field '{name}': {type(value)}")
        result += part
    if len(result) < bytes_in_one_block:
        result += b"\x00" * (bytes_in_one_block - len(result))
    return result

# Writable blocks
block_1 = convert_data_to_writable_16_bytes(2,2,3,3,3,2,1,data_ver = 1, sig_offset = 40, batt_volt_max =25200, batt_volt_min = 22000, batt_total_cap = 22000, batt_c_rat = 10, bind_type = 1 )
block_2 = convert_data_to_writable_16_bytes(8,8,bat_chem_type = "Li-ion",vendor_id="Vendor_1" )
block_4 = convert_data_to_writable_16_bytes(1,2,2,3,1,7,cell_count = 6 ,cell_volt_max = 4200 ,cell_volt_min = 3700 ,cell_cap = 22000 ,cell_c_rat = 10,cell_config = "1S6P")
block_5 = convert_data_to_writable_16_bytes(16,vendor_nm = "Robu")
block_6 = convert_data_to_writable_16_bytes(8,8,oem_id = "12AB_34",batt_id = "AG365_09")
block_8 = convert_data_to_writable_16_bytes(16,oem_nm = "Tattu_oem")
block_9 = convert_data_to_writable_16_bytes(16,bat_nm = "Tattu Battery")
block_10 = convert_data_to_writable_16_bytes(2,2,2,2,bat_len = 250 , bat_wid = 90 , bat_hgt = 60 , bat_wt = 250 )
block_12 = convert_data_to_writable_16_bytes(8,bat_con = "XT-90")
block_16 = convert_data_to_writable_16_bytes(16,bind_info_1 = "bind_Info_1") 
block_17 = convert_data_to_writable_16_bytes(16,bind_info_2 = "bind_Info_2")
block_18 = convert_data_to_writable_16_bytes(16,bind_info_3 = "bind_Info_3")

# 4 Signature blocks only
block_40 = b"" 
block_41 = b"" 
block_42 = b"" 
block_44 = b"" 

# FIXED: 16 blocks total (12 data + 4 signature)
writable_block_list_contents = [block_1, block_2, block_4, block_5, block_6, block_8, block_9, block_10, block_12, block_16, block_17, block_18, block_40, block_41, block_42, block_44]
writable_block_list_index = [1,2,4,5,6,8,9,10,12,16,17,18,40,41,42,44]

if uid:
    print("Found Uid",end = " = ")
    for i in uid:
        print(hex(i),end = " ")
    print("")

    # DATA 
    uid_bytes = bytes(uid)
    data = uid_bytes + block_1 + block_2 + block_4 + block_5 + block_6 + block_8 + block_9 + block_10 + block_12 + block_16 + block_17 + block_18
    print(f"data length: {len(data)} bytes")

    # RSA METHOD
    digest = SHA256.new()
    digest.update(data)  # Sign the FULL data (not just checksum)
    print(f"data hash: {digest.hexdigest()}")

    # Load private key 
    with open("private_key.pem", "r") as f:
        private_key = RSA.importKey(f.read())

    # Sign  - FIXED 64 bytes
    signer = PKCS1_v1_5.new(private_key)
    signature = signer.sign(digest)[:64]  # EXACTLY 64 bytes for 4 blocks
    print(f"RSA signature length: {len(signature)} bytes")

    # Self-verify (BOSS's public key method)
    public_key = private_key.publickey()
    verifier = PKCS1_v1_5.new(public_key)
    try:
        verifier.verify(digest, signature)
        print("VERIFICATION PASSED - RSA method!")
    except:
        print("VERIFICATION FAILED!")

    # Split EXACTLY 64 bytes to 4 blocks
    block_40 = signature[0:16]
    block_41 = signature[16:32]
    block_42 = signature[32:48]
    block_44 = signature[48:64]

    # Update signature blocks
    writable_block_list_contents[-4:] = [block_40, block_41, block_42, block_44]

    # Write all blocks 
    for block_index,block_contents in zip(writable_block_list_index, writable_block_list_contents):
        print(f"Block {block_index}: {block_contents}") #block_contents.hex() - for hex
        write_block_func(block_index,block_contents)
        
else:
    print("Not found Uid")
