
import board, busio, time
from adafruit_pn532.i2c import PN532_I2C
from digitalio import DigitalInOut, Direction

i2c = busio.I2C(board.SCL, board.SDA)
reset_pin = DigitalInOut(board.D23)
req_pin = DigitalInOut(board.D24)
reset_pin.direction = Direction.OUTPUT
req_pin.direction = Direction.OUTPUT

reset_pin.value = False
time.sleep(1)
reset_pin.value = True
time.sleep(1)

pn532 = PN532_I2C(i2c, debug=False, reset=reset_pin, req=req_pin)
pn532.SAM_configuration()
print("DIRECT PN532:", [hex(i) for i in pn532.read_passive_target(timeout=5)])
