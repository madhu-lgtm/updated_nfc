import time
import board
import busio
from digitalio import DigitalInOut
from adafruit_pn532.i2c import PN532_I2C
from pymavlink import mavutil
import RPi.GPIO as GPIO

# Pin Setup:
GPIO.setmode(GPIO.BCM)        # Broadcom pin-numbering scheme
GPIO.setup(18, GPIO.OUT)      # Set GPIO18 as output

# RFID UIDs
uid1_dec = 399535621
uid2_dec = 220492806
uid3_dec = 3321787910

# MAVLink connection to Cube Orange (adjust port/baud as needed)
master = mavutil.mavlink_connection('/dev/serial0', baud=921600)
master.wait_heartbeat()  # Wait for FC heartbeat
print("Connected to flight controller")


def send_status_text(severity, text):
    master.mav.statustext_send(severity, text.encode('utf-8'), len(text))


def read_rfid_tags():
    I2C_FREQ = 100000
    reset_pin = DigitalInOut(board.D23)
    req_pin = DigitalInOut(board.D24)
    i2c = busio.I2C(board.SCL, board.SDA, frequency=I2C_FREQ)
    pn532 = PN532_I2C(i2c, debug=False, reset=reset_pin, req=req_pin)
    pn532.SAM_configuration()

    try:
        while True:
            uid = pn532.read_passive_target(timeout=0.5)
            if uid:
                uid_hex_str = "".join([f"{i:02X}" for i in uid])
                bytes_obj = bytes.fromhex(uid_hex_str)
                uid_hex = bytes_obj.hex()
                uid_dec = int(uid_hex, 16)
                print(f"uid = {uid_dec}")  # Keep local console output
                send_status_text(6, f"UID: {uid_dec}")  # MAV_SEVERITY_INFO=6

                if uid_dec == uid1_dec or uid_dec == uid2_dec:
                    msg = "Authorized Battery"
                    print(msg)
                    send_status_text(0, msg)  # MAV_SEVERITY_NOTICE=4 (green)
                    GPIO.output(18, GPIO.HIGH)  # Output high (3.3 V)
                else:
                    msg = "Unauthorized Battery"
                    print(msg)
                    send_status_text(0, msg)  # MAV_SEVERITY_WARNING=2 (orange)
                    GPIO.output(18, GPIO.LOW)
            else:
                # Optional: reduce spam
                GPIO.output(18, GPIO.LOW)
                print("Waiting for the tag")
            time.sleep(0.3)
    except KeyboardInterrupt:
        print("KeyboardInterrupt")
    finally:
        master.close()


if __name__ == "__main__":
    read_rfid_tags()