from machine import I2C, Pin
import urequests as requests
import ujson
import LSM6DSO
import math
import time


# this is the identifier used by the backend. MUST be unique
BOTTLE_NAME = "bottle_1"

BACKEND_URL = "https://19af-2607-f140-400-60-c4ca-302e-2368-53d7.ngrok-free.app/"


# imu setup
i2c = I2C(1, scl=Pin(12), sda=Pin(13))
imu = LSM6DSO.LSM6DSO(i2c)

# indicator led setup
bottle_empty_led = Pin(15, Pin.OUT)
bottle_empty_led.value(0)


amount_of_water = 100


### reset data in the backend before starting ###
print(f"resetting the backend data for {BOTTLE_NAME}")

url = f"{BACKEND_URL}/reset_data"
headers = {'Content-Type': 'application/json'}
data = ujson.dumps({"bottle_name": BOTTLE_NAME})
try:
    response = requests.post(
        url,
        headers=headers,
        data=data
    )
    print("Status Code:", response.status_code)
    print("Content:", response.text[:500])  # only print the first 500 characters
    response.close()
except Exception as e:
    print("Request failed:", e)

# uploads a single data point to the backend
def upload_data(dp):
    url = f"{BACKEND_URL}/upload_data"
    headers = {'Content-Type': 'application/json'}
    data = ujson.dumps({
        "bottle_name": BOTTLE_NAME,
        "data": [dp],
    })
    try:
        response = requests.post(
            url,
            headers=headers,
            data=data
        )
        response.close()
    except Exception as e:
        print("failure uploading data:", e)
    
    
    

def get_tilt_angles():
    ax = imu.ax() / 1000  # convert from mg to g
    ay = imu.ay() / 1000
    az = imu.az() / 1000

    # Calculate pitch and roll (in degrees)
    pitch = math.atan2(-ax, math.sqrt(ay**2 + az**2)) * 180 / math.pi
    roll = math.atan2(ay, az) * 180 / math.pi
    return pitch, roll


# Main loop
while True:
    if amount_of_water > 0:
        print("amount of water: ", amount_of_water)
    else:
        print("you finished the water bottle! You are hydrated yay!")
    pitch, roll = get_tilt_angles()
    #print("Pitch: {:.2f}°, Roll: {:.2f}°".format(pitch, roll))
    
    if (pitch > 0 and pitch < 15):
        amount_of_water -= 5
    elif (pitch > 15 and pitch < 30):
        amount_of_water -= 7
    elif (pitch > 30 and pitch < 45):
        amount_of_water -= 8
    elif (pitch > 45 and pitch):
        amount_of_water -= 20
        
    if (amount_of_water <= 0):
        bottle_empty_led.value(1)
        
    if amount_of_water < 0:
        amount_of_water = 0
    
    if (amount_of_water == 0):
        bottle_empty_led.value(1)
        
    upload_data(amount_of_water)
        
    
    
