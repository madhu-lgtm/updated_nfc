''' Below Proghram Reads complete memory of the mifare classic 1k card'''
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


uid = pn532.read_passive_target(timeout=0.5)
key_a = b"\xFF\xFF\xFF\xFF\xFF\xFF"
tail_block_list = [3,7,11,15,19,23,27,31,35,39,43,47,51,55,59,63]
text = "Marut Drones" #must be less that <= 16 bytes/char


def read_all_block_func():
    block_num = 1
    if pn532.mifare_classic_authenticate_block(uid,block_num,nfc.MIFARE_CMD_AUTH_A, key_a):
        for block in range(0,64,1):
            block_contents = pn532.mifare_classic_read_block(block)
            if block_contents:
                print(f"\nContents at block {block} = {block_contents}")
            if block in tail_block_list:
                next_tail_block = block+4
                if not pn532.mifare_classic_authenticate_block(uid,next_tail_block,nfc.MIFARE_CMD_AUTH_A,key_a):
                    print("Failed to authenticate in tail block condition in read_all_block_func")                
    else:
        print("Failed to authenticate in read_all_block_func")
        
def read_block_func(read_block_num):

    if pn532.mifare_classic_authenticate_block(uid,read_block_num,nfc.MIFARE_CMD_AUTH_A,key_a):
        block_contents = pn532.mifare_classic_read_block(read_block_num)
        if block_contents:
            print(f"Contents at block {read_block_num} = {block_contents}")
        else:
            print(f"Read block {read_block_num} Failed")
    else:
        print("Failed to authenticate in read_block_func")
    
def write_block_func(write_block_num):

    if pn532.mifare_classic_authenticate_block(uid,write_block_num,nfc.MIFARE_CMD_AUTH_A,key_a):

        raw = text.encode("utf-8")[:16]
        
        if len(raw) < 16:
            raw = raw + b"\x00" * (16-len(raw)) # padding to ensure 16 bytes
        if pn532.mifare_classic_write_block(write_block_num,raw):
            print("Write Ok")
        else:
            print("Write fail")    
    else:
        print("Failed to authenticate in write_block_func")
        

if uid:
    print("Found Uid",end = " = ")
    for i in uid:
        print(hex(i),end = " ") #printing in hex format
    read_all_block_func()
        
else:
    print("Not found Uid")       

