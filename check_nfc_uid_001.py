import time
import board
import busio
from digitalio import DigitalInOut
from adafruit_pn532.i2c import PN532_I2C

reset_pin = DigitalInOut(board.D23)
req_pin = DigitalInOut(board.D24)

i2c = busio.I2C(board.SCL,board.SDA)

pn532 = PN532_I2C(i2c, debug = False, reset = reset_pin, req = req_pin)

pn532.SAM_configuration()

uid = pn532.read_passive_target(timeout = 0.5)

msg = "No Card"
if uid:
    print(uid)
else:
    print(msg)
    
