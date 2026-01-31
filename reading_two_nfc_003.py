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

reset_pin = DigitalInOut(board.D23)
req_pin= DigitalInOut(board.D24)
#i2c = busio.I2C(board.SCL, board.SDA)
pn532 = PN532_I2C(channel_0, debug=False, reset=reset_pin, req=req_pin)
pn532.SAM_configuration()


key_a = b"\xFF\xFF\xFF\xFF\xFF\xFF"

uid = pn532.read_passive_target(timeout=1.0) #Read UID

if uid :
    print(uid)


