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
    def __init__(self,data_ver,sig_offset,batt_volt_max,batt_volt_min,batt_total_cap,batt_c_rat,bind_info):
        self.data_ver = data_ver #2bytes (0,1)
        self.sig_offset = sig_offset #2 bytes (2,3)
        self.batt_volt_max = batt_volt_max #3 bytes (4,5,6)
        self.batt_volt_min = batt_volt_min #3 bytes (7,8,9)
        self.batt_total_cap = batt_total_cap #3 bytes (10,11,12)
        self.batt_c_rat = batt_c_rat #2 bytes (13,14)
        self.bind_info = bind_info #1 byte (15)
        
        self.data_ver_bytes = b""
        self.sig_offset_bytes = b""
        self.batt_volt_max_bytes = b""
        self.batt_volt_min_bytes = b""
        self.batt_total_cap_bytes = b""
        self.batt_c_rat_bytes = b""
        self.bind_info_bytes = b""

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
    
    def get_bind_info_bytes(self) -> bytes:
        #Assuming bind info is type <int>
        data_str = f"{self.bind_info:02x}"
        data_bind_byte1 = bytes.fromhex(data_str)
        self.bind_info_bytes = data_bind_byte1
        return self.bind_info_bytes

    def get_block1_bytes(self) -> bytes:
        #Calling all above methos in series order from top to bottom (can be interchangable if required)
        self.block1_bytes = self.get_data_ver_bytes() + self.get_sig_offset_bytes() + self.get_batt_volt_max_bytes() + self.get_batt_volt_min_bytes() + self.get_batt_total_cap_bytes() + self.get_batt_c_rat_bytes() + self.get_bind_info_bytes()
        return self.block1_bytes


bat1 = Battery_id_maker_block1(65535,40,25200,22000,22000,10,1)
block1_bytes = bat1.get_block1_bytes()

print(f"Block1 bytes = {block1_bytes}")

count = 0
for byte in block1_bytes:
    print(byte)
    if count == 0:
        data_str_0 = f"{byte:02x}"  # Cleanest: direct formatting
    if count == 1:
        data_str_1 = f"{byte:02x}"
        data_ver_str = data_str_0 + data_str_1
        print(f"data ver int = {int(data_ver_str,16)}")  # 65535 ✓
    count += 1


# count = 0
# data_str_0 = ""
# data_str_1 = ""
# for byte in block1_bytes:
#     print(byte)
#     if count == 0 :
#         data_str_0 = str(hex(byte))
#     if count == 1 :
#         data_str_1 = str(hex(byte))
#         data_ver_str = data_str_0 + data_str_1
#         print(f"data ver int = {int(data_ver_str,16)}")
#         #print(type(data_ver_str))
#     count+=1




# data_hex = block1_bytes.hex()
# print(f"{int(data_hex,16)}")








        