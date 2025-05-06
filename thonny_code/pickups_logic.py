from machine import I2C, Pin
import urequests as requests
import ujson
import LSM6DSO
import math
import time
import ntptime

# imu setup
i2c = I2C(1, scl=Pin(12), sda=Pin(13))
imu = LSM6DSO.LSM6DSO(i2c)

BACKEND_URL = "https://09c8-2607-f140-400-60-59e2-cb12-e25-4b2c.ngrok-free.app" # THIS MAY NEED TO BE CHANGED
BOTTLE_NAME = "manuel" # can be anything

def get_tilt_angles():
    ax = imu.ax() / 1000  # convert from mg to g
    ay = imu.ay() / 1000
    az = imu.az() / 1000

    # Calculate pitch and roll (in degrees)
    pitch = math.atan2(-ax, math.sqrt(ay**2 + az**2)) * 180 / math.pi
    roll = math.atan2(ay, az) * 180 / math.pi
    return pitch * -1, roll

def upload_data(dp):
    url = f"{BACKEND_URL}/upload_data"
    
    headers = {'Content-Type': 'application/json'}
    data = ujson.dumps({
        "bottle_name": BOTTLE_NAME,
        "data": dp,
    })
    try:
        ntptime.settime()
        response = requests.post(
            f"{BACKEND_URL}/upload_data",
            headers=headers,
            data=ujson.dumps({
                "bottle_name": BOTTLE_NAME,
                "duration": dp,
                "timestamp": time.localtime()
            })
        )
        response.close()
        
        if response.status_code == 200:
            print("success uploading data")
        
    except Exception as e:
        print("failure uploading data:", e)
        
def reset_data():
    url = f"{BACKEND_URL}/reset_data"
    headers = {'Content-Type': 'application/json'}
    data = ujson.dumps({"bottle_name": BOTTLE_NAME})
    response = requests.post(
        url,
        headers=headers,
        data=data
    )
    print("Status Code:", response.status_code)
    print("Content:", response.text[:500])  # only print the first 500 characters
    response.close()
    
    assert response.status_code == 200, "wifi is bad, please try again"
    


pickups = 0

start_pickup_time = 0 # timestamp when the last pickup began
end_pickup_time = 0 # timestamp when the last pick up ended

in_pickup = False

min_pickup_interval = 1000 # minimum time between intervals (ms)

min_pickup_length = 500 # minimum length of drinking to be considered a pickup

pickup_pitch_th = 45 # pitch threshold to be considered a valid pickup

while True:
    curr_time = time.ticks_ms()
    pitch, _ = get_tilt_angles()
    
    if in_pickup:
        if pitch > pickup_pitch_th:
            
            if (curr_time - start_pickup > min_pickup_length):
                print(f"pickup completed. drank water for {(curr_time - start_pickup) / 1000} s")
                upload_data((curr_time - start_pickup) / 1000)
                pickups += 1
            
            end_pickup_time = curr_time
            in_pickup = False
        
    else:
        since_last_pickup = curr_time - end_pickup_time

        if (since_last_pickup >= min_pickup_interval and pitch <= pickup_pitch_th):
            print("pickup started")
            in_pickup = True
            start_pickup = curr_time
    
    time.sleep(0.1)
