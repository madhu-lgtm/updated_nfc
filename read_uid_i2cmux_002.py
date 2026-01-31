import board
import busio
from adafruit_tca9548a import TCA9548A

import time
from adafruit_pn532.i2c import PN532_I2C
import adafruit_pn532.adafruit_pn532 as nfc
from digitalio import DigitalInOut

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

uid2 =pn532_2.read_passive_target(timeout=1.0) #Read UID
uid = pn532.read_passive_target(timeout=1.0) #Read UID

if uid :
    print([hex(i) for i in uid])
else:
    print("uid1 not found")

if uid2 :
    print([hex(i) for i in uid2])
else:
    print("uid2 not found")


