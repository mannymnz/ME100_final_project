from machine import I2C, Pin
import urequests as requests
import ujson
import LSM6DSO
import math
import time

# imu setup
i2c = I2C(1, scl=Pin(12), sda=Pin(13))
imu = LSM6DSO.LSM6DSO(i2c)

def get_tilt_angles():
    ax = imu.ax() / 1000  # convert from mg to g
    ay = imu.ay() / 1000
    az = imu.az() / 1000

    # Calculate pitch and roll (in degrees)
    pitch = math.atan2(-ax, math.sqrt(ay**2 + az**2)) * 180 / math.pi
    roll = math.atan2(ay, az) * 180 / math.pi
    return pitch * -1, roll


while True:
    print(get_tilt_angles())
    
    time.sleep(0.1)