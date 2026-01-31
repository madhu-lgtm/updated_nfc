
#Updated Program to read two NFC readers
#Working_2
#Included Red Led indication for every read and Solied Green Once verified the tag

import time
import board
import busio
from digitalio import DigitalInOut
from adafruit_pn532.i2c import PN532_I2C
import adafruit_pn532.adafruit_pn532 as nfc
from Crypto.Hash import SHA256
from Crypto.Signature import PKCS1_v1_5
from Crypto.PublicKey import RSA
import RPi.GPIO as GPIO
from adafruit_tca9548a import TCA9548A


buzz_pin = 4
red_led_pin = 14
right_grn_led_pin = 15
left_grn_led_pin = 16
ic_switch_pin = 18


# Pin Setup:
GPIO.setmode(GPIO.BCM)        # Broadcom pin-numbering scheme
GPIO.setup(ic_switch_pin, GPIO.OUT)      # Set GPIO18 as output for relay
GPIO.setup(buzz_pin, GPIO.OUT)      # buzz pin
GPIO.setup(red_led_pin, GPIO.OUT)      # Red Led
GPIO.setup(right_grn_led_pin, GPIO.OUT)      # Right Green Led

#GPIO.output(18, GPIO.LOW)     # Set initially low , initial=GPIO.LOW

# Initialize I2C and TCA9548A multiplexer
i2c = busio.I2C(board.SCL, board.SDA)
tca = TCA9548A(i2c)

# Access a specific I2C channel (e.g., channel 0)
channel_0 = tca[0]
channel_1 = tca[1]

reset_pin = DigitalInOut(board.D23)
req_pin= DigitalInOut(board.D24)
pn532 = PN532_I2C(channel_0, debug=False, reset=reset_pin, req=req_pin)
pn532.SAM_configuration()

reset_pin_2 = DigitalInOut(board.D20)
req_pin_2 = DigitalInOut(board.D21)
pn532_2 = PN532_I2C(channel_1, debug=False, reset=reset_pin_2, req=req_pin_2)
pn532_2.SAM_configuration()

key_a = b"\xFF\xFF\xFF\xFF\xFF\xFF"

# SAME BLOCKS as writer (12 data + 8 signature)
data_block_indices = [1,2,4,5,6,8,9,10,12,16,17,18]
signature_block_indices = [40,41,42,44,45,46,48,49]  # 8 blocks = 128 bytes

def read_block_func(block_index):
    if pn532.mifare_classic_authenticate_block(uid, block_index, nfc.MIFARE_CMD_AUTH_A, key_a):
        block_data = pn532.mifare_classic_read_block(block_index)
        if block_data:
            return bytes(block_data)
    print(f"Reader1_Read failed: Block {block_index}")
    return None

def read_block_func_2(block_index):
    if pn532_2.mifare_classic_authenticate_block(uid, block_index, nfc.MIFARE_CMD_AUTH_A, key_a):
        block_data = pn532_2.mifare_classic_read_block(block_index)
        if block_data:
            return bytes(block_data)
    print(f"Reader2_Read failed: Block {block_index}")
    return None

def read_rfid_tags():

    GPIO.output(red_led_pin, GPIO.HIGH)

    global uid
    uid = pn532.read_passive_target(timeout=1.0)

    if uid:
        print("Reader1_Tag found! UID =", [hex(i) for i in uid])
        uid_bytes = bytes(uid)
        
        # Read data blocks
        print("\nReader1__Reading data blocks...")
        data_blocks = []
        for block_idx in data_block_indices:
            block_data = read_block_func(block_idx)
            if block_data:
                print(f" Reader1_Block {block_idx}: {block_data}") #block_data.hex()[:24]
                data_blocks.append(block_data)
            else:
                print("Reader1_Data read failed!")
                GPIO.output(red_led_pin, GPIO.HIGH)
                GPIO.output(buzz_pin, GPIO.HIGH)
                time.sleep(0.25)
                GPIO.output(red_led_pin, GPIO.LOW)
                GPIO.output(buzz_pin, GPIO.LOW)
                time.sleep(0.25)

                GPIO.output(red_led_pin, GPIO.HIGH)
                GPIO.output(buzz_pin, GPIO.HIGH)
                time.sleep(0.25)
                GPIO.output(red_led_pin, GPIO.LOW)
                GPIO.output(buzz_pin, GPIO.LOW)

                exit(1)
        
        # Read signature blocks (8 blocks = 128 bytes)
        print("\nReader1_Reading signature blocks...")
        sig_blocks = []
        for block_idx in signature_block_indices:
            block_data = read_block_func(block_idx)
            if block_data:
                print(f"  Reader1_Block {block_idx}: {block_data}") #block_data.hex()
                sig_blocks.append(block_data)
            else:
                print("Reader1_Signature read failed!")
                GPIO.output(red_led_pin, GPIO.HIGH)
                GPIO.output(buzz_pin, GPIO.HIGH)
                time.sleep(0.25)
                GPIO.output(red_led_pin, GPIO.LOW)
                GPIO.output(buzz_pin, GPIO.LOW)
                time.sleep(0.25)

                GPIO.output(red_led_pin, GPIO.HIGH)
                GPIO.output(buzz_pin, GPIO.HIGH)
                time.sleep(0.25)
                GPIO.output(red_led_pin, GPIO.LOW)
                GPIO.output(buzz_pin, GPIO.LOW)
                exit(1)
        
        # Rebuild EXACT data
        data = uid_bytes + b''.join(data_blocks)
        print(f"\nReader1_Data length: {len(data)} bytes")
        
        # hash method
        digest = SHA256.new()
        digest.update(data)
        print(f"Reader1_Data hash: {digest.hexdigest()}")
        
        # Rebuild FULL 128-byte signature
        signature = b''.join(sig_blocks)
        print(f"Reader1_Full signature: {len(signature)} bytes")
        
        # Load public key 
        with open("public_key.pem", "r") as f:
            public_key = RSA.importKey(f.read())
        print("Reader1_Public key loaded")
        
        # verification
        print("\nReader1_RSA verification...")
        verifier = PKCS1_v1_5.new(public_key)
        try:
            verified = verifier.verify(digest, signature)
            if verified:
                GPIO.output(right_grn_led_pin, GPIO.HIGH)
                switch_state = GPIO.input(ic_switch_pin) # Check the IC switch pin state
                if switch_state == GPIO.LOW:
                    GPIO.output(buzz_pin, GPIO.HIGH)
                    time.sleep(0.4)
                    GPIO.output(buzz_pin, GPIO.LOW)
                    
                GPIO.output(ic_switch_pin, GPIO.HIGH)  # Output high (3.3 V)

                print("Reader1_VERIFICATION PASSED! Connecting RC Controls to the drone")
                
                # Battery info
                block1 = data_blocks[0]
                data_ver = int.from_bytes(block1[0:2], 'big')
                batt_volt_max = int.from_bytes(block1[4:7], 'big')
                #print(block1)
                print(f"Reader1_Version: {data_ver}")
                print(f"Reader1_Max voltage: {batt_volt_max} mV")
            else:
                print("Reader1_Signature invalid!")

        except Exception as e:
            print("Reader1_Verification error!")
            print(f"Reader1_Error: {e}")

    else:
        print("Reader1_No tag!")
    
    GPIO.output(red_led_pin, GPIO.LOW)

def read_rfid_tags_2():

    GPIO.output(red_led_pin, GPIO.HIGH)

    global uid2
    uid2 = pn532_2.read_passive_target(timeout=1.0)

    if uid2:
        print("Reader2_Tag found! UID =", [hex(i) for i in uid2])
        uid_bytes = bytes(uid2)
        
        # Read data blocks
        print("\nReader2__Reading data blocks...")
        data_blocks = []
        for block_idx in data_block_indices:
            block_data = read_block_func(block_idx)
            if block_data:
                print(f" Reader2_Block {block_idx}: {block_data}") #block_data.hex()[:24]
                data_blocks.append(block_data)
            else:
                print("Reader2_Data read failed!")
                GPIO.output(red_led_pin, GPIO.HIGH)
                GPIO.output(buzz_pin, GPIO.HIGH)
                time.sleep(0.25)
                GPIO.output(red_led_pin, GPIO.LOW)
                GPIO.output(buzz_pin, GPIO.LOW)
                time.sleep(0.25)

                GPIO.output(red_led_pin, GPIO.HIGH)
                GPIO.output(buzz_pin, GPIO.HIGH)
                time.sleep(0.25)
                GPIO.output(red_led_pin, GPIO.LOW)
                GPIO.output(buzz_pin, GPIO.LOW)

                exit(1)
        
        # Read signature blocks (8 blocks = 128 bytes)
        print("\nReader2_Reading signature blocks...")
        sig_blocks = []
        for block_idx in signature_block_indices:
            block_data = read_block_func(block_idx)
            if block_data:
                print(f"  Reader2_Block {block_idx}: {block_data}") #block_data.hex()
                sig_blocks.append(block_data)
            else:
                print("Reader2_Signature read failed!")
                GPIO.output(red_led_pin, GPIO.HIGH)
                GPIO.output(buzz_pin, GPIO.HIGH)
                time.sleep(0.25)
                GPIO.output(red_led_pin, GPIO.LOW)
                GPIO.output(buzz_pin, GPIO.LOW)
                time.sleep(0.25)

                GPIO.output(red_led_pin, GPIO.HIGH)
                GPIO.output(buzz_pin, GPIO.HIGH)
                time.sleep(0.25)
                GPIO.output(red_led_pin, GPIO.LOW)
                GPIO.output(buzz_pin, GPIO.LOW)
                exit(1)
        
        # Rebuild EXACT data
        data = uid_bytes + b''.join(data_blocks)
        print(f"\nReader2_Data length: {len(data)} bytes")
        
        # hash method
        digest = SHA256.new()
        digest.update(data)
        print(f"Reader2_Data hash: {digest.hexdigest()}")
        
        # Rebuild FULL 128-byte signature
        signature = b''.join(sig_blocks)
        print(f"Reader2_Full signature: {len(signature)} bytes")
        
        # Load public key 
        with open("public_key.pem", "r") as f:
            public_key = RSA.importKey(f.read())
        print("Reader2_Public key loaded")
        
        # verification
        print("\nReader2_RSA verification...")
        verifier = PKCS1_v1_5.new(public_key)
        try:
            verified = verifier.verify(digest, signature)
            if verified:
                GPIO.output(right_grn_led_pin, GPIO.HIGH)
                switch_state = GPIO.input(ic_switch_pin) # Check the IC switch pin state
                if switch_state == GPIO.LOW:
                    GPIO.output(buzz_pin, GPIO.HIGH)
                    time.sleep(0.4)
                    GPIO.output(buzz_pin, GPIO.LOW)
                    
                GPIO.output(ic_switch_pin, GPIO.HIGH)  # Output high (3.3 V)

                print("Reader2_VERIFICATION PASSED! Connecting RC Controls to the drone")
                
                # Battery info
                block1 = data_blocks[0]
                data_ver = int.from_bytes(block1[0:2], 'big')
                batt_volt_max = int.from_bytes(block1[4:7], 'big')
                #print(block1)
                print(f"Reader2_Version: {data_ver}")
                print(f"Reader2_Max voltage: {batt_volt_max} mV")
            else:
                print("Reader2_Signature invalid!")

        except Exception as e:
            print("Reader2_Verification error!")
            print(f"Reader2_Error: {e}")

    else:
        print("Reader2_No tag!")
    
    GPIO.output(red_led_pin, GPIO.LOW)


if __name__ == "__main__":
    
    read_rfid_tags()
    read_rfid_tags_2()

    
    