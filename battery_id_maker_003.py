# import time 
# import busio
# import board
# from adafruit_pn532.i2c import PN532_I2C
# from digitalio import DigitalInOut
# import adafruit_pn532.adafruit_pn532 as nfc

# reset_pin = DigitalInOut(board.D23)
# req_pin = DigitalInOut(board.D24)

# i2c = busio.I2C(board.SCL,board.SDA)

# pn532 = PN532_I2C(i2c, debug = False, reset = reset_pin, req = req_pin)

# pn532.SAM_configuration()


# uid = pn532.read_passive_target(timeout=0.5)
# key_a = b"\xFF\xFF\xFF\xFF\xFF\xFF"
# tail_block_list = [3,7,11,15,19,23,27,31,35,39,43,47,51,55,59,63]

class Battery_id_maker_block1:
    def __init__(self,data_ver,sig_offset,batt_volt_max,batt_volt_min,batt_total_cap,batt_c_rat,bind_type):
        self.data_ver = data_ver #2bytes (0,1)
        self.sig_offset = sig_offset #2 bytes (2,3)
        self.batt_volt_max = batt_volt_max #3 bytes (4,5,6)
        self.batt_volt_min = batt_volt_min #3 bytes (7,8,9)
        self.batt_total_cap = batt_total_cap #3 bytes (10,11,12)
        self.batt_c_rat = batt_c_rat #2 bytes (13,14)
        self.bind_type = bind_type #1 byte (15)
        
        self.data_ver_bytes = b""
        self.sig_offset_bytes = b""
        self.batt_volt_max_bytes = b""
        self.batt_volt_min_bytes = b""
        self.batt_total_cap_bytes = b""
        self.batt_c_rat_bytes = b""
        self.bind_type_bytes = b""

        self.block1_bytes = b""
    
    def get_data_ver_bytes(self) -> bytes:
        #Assuming data version to be <int> type
        data_str = f"{self.data_ver:04x}"
        data_ver_byte_1 = bytes.fromhex(data_str[:2]) #msb
        data_ver_byte_2 = bytes.fromhex(data_str[2:]) #lsb
        
        self.data_ver_bytes = data_ver_byte_1 + data_ver_byte_2
        #print(self.data_ver_bytes)
        #print(type(self.data_ver_bytes))

        return self.data_ver_bytes
    
    def get_sig_offset_bytes(self) -> bytes:
        #Assuming sig offset to be <int> type
        data_str = f"{self.sig_offset:04x}"
        data_sig_byte_1 = bytes.fromhex(data_str[:2]) #msb
        data_sig_byte_2 = bytes.fromhex(data_str[2:]) #lsb
        self.sig_offset_bytes = data_sig_byte_1 + data_sig_byte_2
        return self.sig_offset_bytes
    
    def get_batt_volt_max_bytes(self) -> bytes:
        #Assuming batt volt max is type <int> in milli volts
        data_str = f"{self.batt_volt_max:06x}"
        data_batt_max_byte_1 = bytes.fromhex(data_str[:2]) #msb
        data_batt_max_byte_2 = bytes.fromhex(data_str[2:4])
        data_batt_max_byte_3 = bytes.fromhex(data_str[4:]) #lsb
        self.batt_volt_max_bytes = data_batt_max_byte_1 + data_batt_max_byte_2 + data_batt_max_byte_3
        return self.batt_volt_max_bytes
    
    def get_batt_volt_min_bytes(self) -> bytes:
        #Assuming batt volt min is type <int> in milli volts
        data_str = f"{self.batt_volt_min:06x}"
        data_batt_min_byte_1 = bytes.fromhex(data_str[:2]) #msb
        data_batt_min_byte_2 = bytes.fromhex(data_str[2:4])
        data_batt_min_byte_3 = bytes.fromhex(data_str[4:]) #lsb
        self.batt_volt_min_bytes = data_batt_min_byte_1 + data_batt_min_byte_2 + data_batt_min_byte_3
        return self.batt_volt_min_bytes
    
    def get_batt_total_cap_bytes(self) -> bytes:
        #Assuming batt capacity is type <int> in milli amp hour
        data_str = f"{self.batt_total_cap:06x}"
        data_cap_byte1 = bytes.fromhex(data_str[:2]) #msb
        data_cap_byte2 = bytes.fromhex(data_str[2:4])
        data_cap_byte3 = bytes.fromhex(data_str[4:]) #lsb
        self.batt_total_cap_bytes = data_cap_byte1 + data_cap_byte2 + data_cap_byte3
        return self.batt_total_cap_bytes
    
    def get_batt_c_rat_bytes(self) -> bytes:
        #Assuming batt C rating is type <int>
        data_str = f"{self.batt_c_rat:04x}"
        data_c_byte1 = bytes.fromhex(data_str[:2]) #msb
        data_c_byte2 = bytes.fromhex(data_str[2:]) #lsb
        self.batt_c_rat_bytes = data_c_byte1 + data_c_byte2
        return self.batt_c_rat_bytes
    
    def get_bind_type_bytes(self) -> bytes:
        #Assuming bind info is type <int>
        data_str = f"{self.bind_type:02x}"
        data_bind_byte1 = bytes.fromhex(data_str)
        self.bind_type_bytes = data_bind_byte1
        return self.bind_type_bytes

    def get_block1_bytes(self) -> bytes:
        #Calling all above methos in series order from top to bottom (can be interchangable if required)
        self.block1_bytes = self.get_data_ver_bytes() + self.get_sig_offset_bytes() + self.get_batt_volt_max_bytes() + self.get_batt_volt_min_bytes() + self.get_batt_total_cap_bytes() + self.get_batt_c_rat_bytes() + self.get_bind_type_bytes()
        return self.block1_bytes
    #---------------------------------------------------------------------

    def view_block1_info(self) -> None:
        count = 0
        for byte in self.block1_bytes:
            #print(byte)
            # block1_bytyes = (0,1) -> data ver, (2,3) -> sig offset, (4,5,6) -> max milli volt, (7,8,9) -> min milli volt,
            # (10,11,12) -> total mah, (13,14) -> c rate, (15) -> bind info
            match count:
                case 0:
                    data_str_0 = f"{byte:02x}"  
                case 1:
                    data_str_1 = f"{byte:02x}"
                    #print(type(data_str_1))
                    data_ver_str = data_str_0 + data_str_1
                    print(f"data ver = {int(data_ver_str,16)}")

                case 2:
                    data_str_2 = f"{byte:02x}"
                case 3:
                    data_str_3 = f"{byte:02x}"
                    data_sig_str = data_str_2 + data_str_3
                    print(f"sig offset = {int(data_sig_str,16)}")

                case 4: 
                    data_str_4 = f"{byte:02x}"
                case 5:
                    data_str_5 = f"{byte:02x}"
                case 6:
                    data_str_6 = f"{byte:02x}"
                    data_max_mv_str = data_str_4 + data_str_5 + data_str_6
                    print(f"battery max milli volt = {int(data_max_mv_str,16)}")

                case 7: 
                    data_str_7 = f"{byte:02x}"
                case 8:
                    data_str_8 = f"{byte:02x}"
                case 9:
                    data_str_9 = f"{byte:02x}"
                    data_min_mv_str = data_str_7 + data_str_8 + data_str_9
                    print(f"battery min milli volt = {int(data_min_mv_str,16)}")

                case 10: 
                    data_str_10 = f"{byte:02x}"
                case 11: 
                    data_str_11 = f"{byte:02x}"
                case 12: 
                    data_str_12 = f"{byte:02x}"
                    data_total_cap_str = data_str_10 + data_str_11 + data_str_12
                    print(f"battery total capacity mAh = {int(data_total_cap_str,16)}")

                case 13: 
                    data_str_13 = f"{byte:02x}"
                case 14: 
                    data_str_14 = f"{byte:02x}"
                    data_c_rate_str = data_str_13 + data_str_14
                    print(f"battary c rate = {int(data_c_rate_str,16)}")

                case 15: 
                    data_str_15 = f"{byte:02x}"
                    data_bind_type_str = data_str_15
                    print(f"bind type = {int(data_bind_type_str,16)}")
            count += 1

class Battery_id_maker_block2:
    def __init__(self,cell_count,cell_volt_max,cell_volt_min,cell_cap,cell_c_rat,cell_config):
        self.cell_count = cell_count #1 bytes (0)
        self.cell_volt_max = cell_volt_max #2 bytes (1,2)
        self.cell_volt_min = cell_volt_min #2 bytes (3,4)
        self.cell_cap = cell_cap #3 bytes (5,6,7)
        self.cell_c_rat = cell_c_rat #1 bytes (8)
        self.cell_config = cell_config #7 bytes (9,10,11,12,13,14,15)

        self.cell_count_bytes = b""
        self.cell_volt_max_bytes = b""
        self.cell_volt_min_bytes = b""
        self.cell_cap_bytes = b""
        self.cell_c_rat_bytes = b""
        self.cell_config_bytes = b""

        self.block2_bytes = b""

    def get_cell_count_bytes(self) -> bytes:
        data_str = f"{self.cell_count:02x}"
        data_cell_count_byte1 = bytes.fromhex(data_str) 
        self.cell_count_bytes = data_cell_count_byte1 
        return self.cell_count_bytes
    
    def get_cell_volt_max_bytes(self) -> bytes:
        data_str = f"{self.cell_volt_max:04x}"
        data_cell_volt_max_byte1 = bytes.fromhex(data_str[:2])
        data_cell_volt_max_byte2 = bytes.fromhex(data_str[2:])
        self.cell_volt_max_bytes = data_cell_volt_max_byte1 + data_cell_volt_max_byte2
        return self.cell_volt_max_bytes
    
    def get_cell_volt_min_bytes(self) -> bytes:
        data_str = f"{self.cell_volt_min:04x}"
        data_cell_volt_min_byte1 = bytes.fromhex(data_str[:2])
        data_cell_volt_min_byte2 = bytes.fromhex(data_str[2:])
        self.cell_volt_min_bytes = data_cell_volt_min_byte1 + data_cell_volt_min_byte2
        return self.cell_volt_min_bytes 
    
    def get_cell_cap_bytes(self) -> bytes:
        data_str = f"{self.cell_cap:06x}"
        data_cell_cap_byte1 = bytes.fromhex(data_str[:2])
        data_cell_cap_byte2 = bytes.fromhex(data_str[2:4])
        data_cell_cap_byte3 = bytes.fromhex(data_str[4:])
        self.cell_c_rat_bytes = data_cell_cap_byte1 + data_cell_cap_byte2 + data_cell_cap_byte3
        return self.cell_c_rat_bytes
    
    def get_cell_c_rat_bytes(self) -> bytes:
        data_str = f"{self.cell_c_rat:02x}"
        data_cell_c_rat_byte1 = bytes.fromhex(data_str)
        self.cell_c_rat_bytes = data_cell_c_rat_byte1
        return self.cell_c_rat_bytes
    
    def get_cell_config_bytes(self) -> bytes:
        text = self.cell_config.encode("utf-8")[:7]
        if len(text) <= 7 :
            self.cell_config_bytes = text + b"\x00" * (7-len(text)) # padding to ensure 7 bytes
        #print(self.cell_config_bytes)
        return self.cell_config_bytes
    
    def get_block2_bytes(self) -> bytes:
        self.block2_bytes = self.get_cell_count_bytes() + self.get_cell_volt_max_bytes() + self.get_cell_volt_min_bytes() + self.get_cell_cap_bytes() + self.get_cell_c_rat_bytes() + self.get_cell_config_bytes()
        return self.block2_bytes
    
    #-------------------------------------------
    def view_block2_info(self) -> None:
        count = 0
        for byte in self.block2_bytes:
            #print(byte)
            # block2_bytes = (0) -> cell count , (1,2) -> cell max milli volt , (3,4) ->cell min milli volt, (5,6,7) -> cell capacity mAh,
            # (8) -> cell c rate , (9,10,11,12,13,14,15) -> cell configuration
            match count:
                case 0:
                    data_str_0 = f"{byte:02x}"  
                    data_cell_count_str = data_str_0
                    print(f"cell count = {int(data_cell_count_str,16)}")

                case 1:
                    data_str_1 = f"{byte:02x}"
                case 2:
                    data_str_2 = f"{byte:02x}"
                    data_cell_max_volt = data_str_1 + data_str_2
                    print(f"cell max milli volt  = {int(data_cell_max_volt,16)}")

                case 3:
                    data_str_3 = f"{byte:02x}"
                case 4: 
                    data_str_4 = f"{byte:02x}"
                    data_cell_min_volt = data_str_3 + data_str_4
                    print(f"cell min milli volt  = {int(data_cell_min_volt,16)}")

                case 5:
                    data_str_5 = f"{byte:02x}"
                case 6:
                    data_str_6 = f"{byte:02x}"
                case 7: 
                    data_str_7 = f"{byte:02x}"
                    data_cell_cap = data_str_5 + data_str_6 + data_str_7
                    print(f"cell capacity mAh = {int(data_cell_cap,16)}")

                case 8:
                    data_str_8 = f"{byte:02x}"
                    data_cell_c_rat = data_str_8
                    print(f"cell c rate = {int(data_cell_c_rat,16)}")
                case 9:
                    data_str_9 = f"{byte:c}"
                    # print(data_str_9)
                    # print(type(data_str_9))  

                case 10: 
                    data_str_10 = f"{byte:c}"
                case 11: 
                    data_str_11 = f"{byte:c}"
                case 12: 
                    data_str_12 = f"{byte:c}"
                case 13: 
                    data_str_13 = f"{byte:c}"
                case 14: 
                    data_str_14 = f"{byte:c}"
                    #print(data_byte_14)
                case 15: 
                    data_str_15 = f"{byte:c}"
                    data_cell_config_str = data_str_9 + data_str_10 + data_str_11 + data_str_12 + data_str_13 + data_str_14 + data_str_15
                    text = data_cell_config_str.strip("\x00")
                    # print(data_cell_config_str)
                    # print(len(data_cell_config_str))
                    # print(text)
                    # print(len(text))
                    print(f"cell configuration = {text}")                    
            count += 1

class Battery_id_maker_block4: #Should not use block3 memory 
    def __init__(self,batt_chem_type,vendor_id):
        self.batt_chem_type = batt_chem_type #8bytes (0,1,2,3,4,5,6,7)
        self.vendor_id = vendor_id #8bytes (8,9,10,11,12,13,14,15)

        self.batt_chem_type_bytes = b""
        self.vendor_id_bytes = b""

        self.block4_bytes = b""

    def get_batt_chem_type_bytes(self) -> bytes:
        text = self.batt_chem_type.encode("utf-8")[:8]
        if len(text) <= 8 :
            self.batt_chem_type_bytes = text + b"\x00" * (8-len(text)) # padding to ensure 8 bytes
        #print(self.batt_chem_type_bytes)
        return self.batt_chem_type_bytes
        
    def get_vendor_id_bytes(self) -> bytes:
        text = self.vendor_id.encode("utf-8")[:8]
        if len(text) <= 8 :
            self.vendor_id_bytes = text + b"\x00" * (8-len(text)) # padding to ensure 8 bytes
        #print(self.vendor_id_bytes)
        return self.vendor_id_bytes
        
    def get_block4_bytes(self) -> bytes:
        self.block4_bytes = self.get_batt_chem_type_bytes() + self.get_vendor_id_bytes()
        #print(len(self.block4_bytes))
        return self.block4_bytes
    #-------------------------------------------

    def view_block4_info(self) -> None:
        count = 0
        for byte in self.block4_bytes:
            #print(byte)
            # block4_bytes = (0 to 7) -> Battery Chemistry (text), (8 to 15) -> Vendor id (text) 
            match count:
                case 0:
                    data_str_0 = f"{byte:c}"
                case 1:
                    data_str_1 = f"{byte:c}"
                case 2:
                    data_str_2 = f"{byte:c}"
                case 3:
                    data_str_3 = f"{byte:c}"
                case 4:
                    data_str_4 = f"{byte:c}"
                case 5:
                    data_str_5 = f"{byte:c}"
                case 6:
                    data_str_6 = f"{byte:c}"
                case 7:
                    data_str_7 = f"{byte:c}"
                    data_batt_chem_type_str = data_str_0 + data_str_1 + data_str_2 + data_str_3 + data_str_4 + data_str_5 + data_str_6 + data_str_7
                    text1 = data_batt_chem_type_str.strip("\x00")
                    print(f"Battery Chemistry type = {text1}")

                case 8:
                    data_str_8 = f"{byte:c}"
                case 9:
                    data_str_9 = f"{byte:c}"
                case 10:
                    data_str_10 = f"{byte:c}"
                case 11:
                    data_str_11 = f"{byte:c}"
                case 12:
                    data_str_12 = f"{byte:c}"
                case 13:
                    data_str_13 = f"{byte:c}"
                case 14:
                    data_str_14 = f"{byte:c}"
                case 15:
                    data_str_15 = f"{byte:c}"
                    data_vendor_id_str = data_str_8 + data_str_9 + data_str_10 + data_str_11 + data_str_12 + data_str_13 + data_str_14 + data_str_15
                    text2 = data_vendor_id_str.strip("\x00")
                    print(f"Vendor id = {text2}")
            count += 1


#Object Creation for writting to every block of memory
bat1_block1 = Battery_id_maker_block1(data_ver = 65535, sig_offset = 40, batt_volt_max =25200, batt_volt_min = 22000, batt_total_cap = 22000, batt_c_rat = 10, bind_type = 1 )
bat1_block2 = Battery_id_maker_block2(cell_count = 6 ,cell_volt_max = 4200 ,cell_volt_min = 3700 ,cell_cap = 22000 ,cell_c_rat = 10,cell_config = "1S6P")
bat1_block4 = Battery_id_maker_block4(batt_chem_type = "Li-ion",vendor_id="Vendor_1") #input only 8 char each argument


#BLOCK 1 Memory Handling (write raw bytes to memory / view written info on memory after reading from memory)
block1_raw_bytes = bat1_block1.get_block1_bytes() # Returns the block1 bytes , which need to be written later to the Mifare Classic 1k tag
print(f"block1 raw bytes (to be written to memory) = {block1_raw_bytes} and len = {len(block1_raw_bytes)}")
bat1_block1.view_block1_info() # Decodes the information of block1 (used after reading the raw bytes from the Mifare Classic 1k tag block1 Memory)

#BLOCK 2 Memory Handling (write raw bytes to memory / view written info on memory after reading from memory)
block2_raw_bytes = bat1_block2.get_block2_bytes()
print(f"block2 raw bytes (to be written to memory) = {block2_raw_bytes} and len = {len(block2_raw_bytes)}")
bat1_block2.view_block2_info()

#BLOCK 3 (Should not use)
#BLOCK 4 
block4_raw_bytes = bat1_block4.get_block4_bytes()
print(f"block4 raw bytes (to be written to memory) = {block4_raw_bytes} and len = {len(block4_raw_bytes)}")
bat1_block4.view_block4_info()




















        
