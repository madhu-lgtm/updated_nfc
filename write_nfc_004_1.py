''' Below Program to Write the specific Block "text" '''
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
text = "FFff" #must be less that <= 16 bytes/char
bin_text = b"\xff\xFF"
non_writable_block_list = [0,3,7,11,15,19,23,27,31,35,39,43,47,51,55,59,63]

def write_block_func(write_block_num):
    if write_block_num not in non_writable_block_list:
        #print(f"block {write_block_num} is writable")        
        if pn532.mifare_classic_authenticate_block(uid,write_block_num,nfc.MIFARE_CMD_AUTH_A,key_a):

            #raw = text.encode("utf-8")[:16]
            
            #if len(raw) < 16:
            if len(bin_text) < 16:
                raw = bin_text + b"\x00" * (16-len(bin_text)) # padding to ensure 16 bytes
                print(len(raw))
                print(raw)
            if pn532.mifare_classic_write_block(write_block_num,raw):
                print("Write Ok")
            else:
                print("Write fail")    
        else:
            print("Failed to authenticate in write_block_func")
            
    else:
        print(f"block {write_block_num} is Not Writable \nThis are Non Writable Block List {non_writable_block_list} ")

if uid:
    print("Found Uid",end = " = ")
    for i in uid:
        print(hex(i),end = " ") #printing in hex format
    print("")
    write_block_func(1) #from 0 to 63 (excuding 0 and tail Block List)
    
        
else:
    print("Not found Uid")       