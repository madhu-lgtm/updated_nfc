"""
Below Program Reads the contents of the specified block 
 Make sure to place the Mifare Classic 1k Card on the nfc module before running the code
"""

import time 
import busio
import board
from adafruit_pn532.i2c import PN532_I2C
from digitalio import DigitalInOut
import adafruit_pn532.adafruit_pn532 as nfc

reset_pin = DigitalInOut(board.D23)
req_pin = DigitalInOut(board.D24)

i2c = busio.I2C(board.SCL,board.SDA)

pn532 = PN532_I2C(i2c, debug = False, reset = reset_pin, req = req_pin)

pn532.SAM_configuration()

block_num = 3

block_contents = None
uid = pn532.read_passive_target(timeout=0.5)
key_a = b"\xFF\xFF\xFF\xFF\xFF\xFF"

if uid:
    print("Found Uid",end = " = ")
    for i in uid:
        print(hex(i),end = " ") #printing in hex format
    if pn532.mifare_classic_authenticate_block(uid,block_num,nfc.MIFARE_CMD_AUTH_A, key_a):
        block_contents = pn532.mifare_classic_read_block(block_num)
        if block_contents:
            print(f"\nContents at block {block_num} = {block_contents}")
else:
    print("Not found Uid")
    

    
