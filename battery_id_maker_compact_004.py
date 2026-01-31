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
non_writable_block_list = [0,3,7,11,15,19,23,27,31,35,39,43,47,51,55,59,63]

def write_block_func(block_index,block_contents):
    if block_index not in non_writable_block_list:      
        if pn532.mifare_classic_authenticate_block(uid,block_index,nfc.MIFARE_CMD_AUTH_A,key_a):
            if pn532.mifare_classic_write_block(block_index,block_contents):
                print("Write Ok")
            else:
                print("Write fail")    
        else:
            print("Failed to authenticate in write_block_func")            
    else:
        print(f"block {write_block_num} is Not Writable \nThis are Non Writable Block List {non_writable_block_list} ")
   

# Funtion Buit for Convrting the text fields (Ascii) or int fields to bytes (writable format for the NFC Module) 1b bytes at a time
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

# -------------- MAFARE CLASSIC 1K MEMORY BLOCK ENTRY SECTORS (0-15)  -----------------------------------------
#Sector 0
#Block 0 Not Writable (Contains Tag UID information from Manufacturer) -> Sector 0 Start
#Block 1 Writables
block_1 = convert_data_to_writable_16_bytes(2,2,3,3,3,2,1,data_ver = 1, sig_offset = 40, batt_volt_max =25200, batt_volt_min = 22000, batt_total_cap = 22000, batt_c_rat = 10, bind_type = 1 )

#Block 2 Writables
block_2 = convert_data_to_writable_16_bytes(8,8,bat_chem_type = "Li-ion",vendor_id="Vendor_1" )
#Block 3 Not Writable <- Sector 0 End

#Sector 1
#Block 4 Writables -> Sector 1 Start
block_4 = convert_data_to_writable_16_bytes(1,2,2,3,1,7,cell_count = 6 ,cell_volt_max = 4200 ,cell_volt_min = 3700 ,cell_cap = 22000 ,cell_c_rat = 10,cell_config = "1S6P")

#Block 5 Writables 
block_5 = convert_data_to_writable_16_bytes(16,vendor_nm = "Robu")

#Block 6 Writables
block_6 = convert_data_to_writable_16_bytes(8,8,oem_id = "12AB_34",batt_id = "AG365_09")
#BLock 7 Not Writable <- Sector 1 End

#Sector 2
#Block 8 Writables -> Sector 2 Start
block_8 = convert_data_to_writable_16_bytes(16,oem_nm = "Tattu_oem")

#Block 9 Writables  
block_9 = convert_data_to_writable_16_bytes(16,bat_nm = "Tattu Battery")

#Block 10 Writables
block_10 = convert_data_to_writable_16_bytes(2,2,2,2,bat_len = 250 , bat_wid = 90 , bat_hgt = 60 , bat_wt = 250 )
#Block 11 Not Writable <- Sector 2 End

#Sector 3
#Block 12 Writables -> Sector 3 Start
block_12 = convert_data_to_writable_16_bytes(8,bat_con = "XT-90") # Other 8 bytes Reserved

#Block 13, 14 (RESERVED)
#Block 15 Not Writable <- Sector 3 End


#------- Bind info Start (3-Blocks or 48-bytes ) --------------  
#Sector 4
#Block 16 Writables -> Sector 4 Start
block_16= convert_data_to_writable_16_bytes(16,bind_info_1 = "bind_Info_1") 

#Block 17 Writables
block_17 = convert_data_to_writable_16_bytes(16,bind_info_2 = "bind_Info_2")

#Block 18 Writables
block_18 = convert_data_to_writable_16_bytes(16,bind_info_3 = "bind_Info_3")
#-------- Bind info End ----------------
#Block 19 Not Writable <- Sector 4 End

#Sector 5
#Block 20,21,22 (RESERVED)
#Block 23 Not Writable

#Sector 6
#Block 24,25,26 (RESERVED)
#Block 27 Not Writable

#Sector 7
#Block 28,29,30 (RESERVED)
#Block 31 Not Writable

#Sector 8
#Block 32,33,34 (RESERVED)
#Block 35 Not Writable

#Sector 9
#Block 36,37,38 (RESERVED)
#Block 39 Not Writable

#---- Signature Blocks Start (4-Blocks or 64-bytes ) -----------
#Sector 10
#Block 40 Writables -> Sector 10 Start
block_40 = convert_data_to_writable_16_bytes(16,sig_1 = "sig_1") 

#Block 41 Writables
block_41 = convert_data_to_writable_16_bytes(16,sig_2 = "sig_2")

#Block 42 Writables
block_42 = convert_data_to_writable_16_bytes(16,sig_3 = "sig_3")
#Block 43 Not Writables <- Sector 10 End

#Sector 11
#BLock 44 Writable -> Sector 11 Start
block_44 = convert_data_to_writable_16_bytes(16,sig_4 = "sig_4")
#------ Signature Blocks End-------------

#Block 45,46 (RESERVED)
#Block 47 Not Writable <- Sector 11 End

#Sector 12
#Block 48,49,50 (RESERVED)
#Block 51 Not Writable

#Sector 13
#Block 52,53,54 (RESERVED)
#Block 55 Not Writable

#Sector 14
#Block 56,57,58 (RESERVED)
#Block 59 Not Writable

#Sector 15
#Block 60,61,62 (RESERVED)
#Block 63 Not Writable
#----------------------------- END OF MEMORY ENTRTY -------------------------------------

block_rsv = b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00" #16 bytes default data

writable_block_list_contents = [block_1, block_2, block_4, block_5, block_6, block_8, block_9, block_10, block_12, block_16, block_17, block_18, block_40, block_41, block_42, block_44]
writable_block_list_index = [1,2,4,5,6,8,9,10,12,16,17,18,40,41,42,44] 




if uid:
    print("Found Uid",end = " = ")
    for i in uid:
        print(hex(i),end = " ") #printing in hex format
    print("")
    #Concatinate the Uid with data (from block1 to block18)
    data = uid + block_1 + block_2 + block_4 + block_5 + block_6 + block_8 + block_9 + block_10 + block_12 + block_16 + block_17 + block_18
    print (f"data = {data}")

    #Compute Checksum

    #Generate Sig

    #Cut the Sig into writable 1b bytes format (Block40 - 43)
    

    #write_block_func(1) #from 0 to 63 (excuding 0 and tail Block List)
    for block_index,block_contents in zip(writable_block_list_index, writable_block_list_contents):
        print(f"Block {block_index} Writable Contents: {block_contents}")
        #write_block_func(block_index,block_contents)
        pass
else:
    print("Not found Uid")