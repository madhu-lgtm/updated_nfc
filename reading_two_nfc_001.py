import time
import board
import busio
from adafruit_pn532.i2c import PN532_I2C
import adafruit_pn532.adafruit_pn532 as nfc
from digitalio import DigitalInOut

#I2C_FREQ = 100000
# reset_pin = DigitalInOut(board.D23)
# req_pin= DigitalInOut(board.D24)
# #i2c = busio.I2C(board.SCL, board.SDA, frequency=I2C_FREQ)
# i2c = busio.I2C(board.SCL, board.SDA)
# pn532 = PN532_I2C(i2c, debug=False, reset=reset_pin, req=req_pin)
# pn532.SAM_configuration()



reset_pin_2 = DigitalInOut(board.D20)
req_pin_2 = DigitalInOut(board.D21)
#i2c_2 = busio.I2C(board.SCL, board.SDA, frequency=I2C_FREQ)
i2c_2 = busio.I2C(board.SCL, board.SDA)
pn532_2 = PN532_I2C(i2c_2, debug=False, reset=reset_pin_2, req=req_pin_2)
pn532_2.SAM_configuration()

key_a = b"\xFF\xFF\xFF\xFF\xFF\xFF"

#uid = pn532.read_passive_target(timeout=1.0) #Read UID
uid2 =pn532_2.read_passive_target(timeout=1.0) #Read UID

# if uid :
#     print(uid)
if uid2 :
    print(uid2)






