# program for checking firmware version and uid over spi 
import board
import busio
from digitalio import DigitalInOut
from adafruit_pn532.spi import PN532_SPI

# SPI connection:
spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
cs_pin = DigitalInOut(board.D5) #D5 = gpio5
pn532 = PN532_SPI(spi, cs_pin, debug=False)

ic, ver, rev, support = pn532.firmware_version
print(f"Found PN532 with firmware version: {ver}.{rev}",end="\n")

# Configure PN532 to communicate with MiFare cards
pn532.SAM_configuration()

uid = pn532.read_passive_target(timeout=0.5)

# Try again if no card is available.
if uid:
    print("Found card with UID:", [hex(i) for i in uid])
else:
    print("UID Not Found")



