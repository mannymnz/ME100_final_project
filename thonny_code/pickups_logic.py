from machine import I2C, Pin, PWM
import urequests as requests
import ujson
import LSM6DSO
import math
import time

LCD_ENABLED = False

if LCD_ENABLED:
    from i2c_lcd1602 import I2C_LCD1602


# ========== SENSOR SETUP ==========
i2c = I2C(1, scl=Pin(12), sda=Pin(13))
imu = LSM6DSO.LSM6DSO(i2c)

BACKEND_URL = "https://me100-final-project-1.onrender.com/"
BOTTLE_NAME = "tom's bottle"


# lcd screen setup

if LCD_ENABLED:
    screen_i2c = I2C(0, scl=Pin(15), sda=Pin(32))
    lcd = I2C_LCD1602(screen_i2c)

    lcd.clear()
    lcd.puts(BOTTLE_NAME, 0, 0)
    lcd.puts("pickups: 0", 0, 1)

def get_tilt_angles():
    ax = imu.ax() / 1000
    ay = imu.ay() / 1000
    az = imu.az() / 1000
    pitch = math.atan2(-ax, math.sqrt(ay**2 + az**2)) * 180 / math.pi
    roll = math.atan2(ay, az) * 180 / math.pi
    return pitch * -1, roll

def upload_data(dp):
    headers = {'Content-Type': 'application/json'}
    try:
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
    except Exception as e:
        print("failure uploading data:", e)

def reset_data():
    url = f"{BACKEND_URL}/reset_data"
    headers = {'Content-Type': 'application/json'}
    data = ujson.dumps({"bottle_name": BOTTLE_NAME})
    response = requests.post(url, headers=headers, data=data)
    print("Status Code:", response.status_code)
    print("Content:", response.text[:500])
    response.close()

reset_data()

# ========== LED SETUP ==========
led = Pin(33, Pin.OUT)
led.off()  # LED starts off

# ========== SPEAKER SETUP ==========
buzzer = PWM(Pin(27), freq=3520, duty=0)  # initially silent

# ========== PICKUP TRACKING ==========
pickups = 0
start_pickup = time.ticks_ms()
end_pickup_time = time.ticks_ms()
in_pickup = False

min_pickup_interval = 1000  # ms
min_pickup_length = 500     # ms
pickup_pitch_th = 30        # degrees
song_delay = 10000           # ms

note_playing = False
has_started = False

while True:
    curr_time = time.ticks_ms()
    pitch, _ = get_tilt_angles()

    if in_pickup:
        if pitch > pickup_pitch_th:
            led.off()
            if (curr_time - start_pickup > min_pickup_length):
                print(f"pickup completed. drank water for {(curr_time - start_pickup) / 1000} s")
                pickups += 1
                # update the lcd screen
                if LCD_ENABLED:
                    lcd.puts(f"pickups: {pickups}", 0, 1)
                
                upload_data((curr_time - start_pickup) / 1000)
                

            end_pickup_time = time.ticks_ms()
            in_pickup = False
            note_playing = False
    else:
        since_last_pickup = curr_time - end_pickup_time

        if (since_last_pickup >= min_pickup_interval and pitch <= pickup_pitch_th):
            buzzer.duty(0)
            print("pickup started")
            in_pickup = True
            start_pickup = curr_time
            
        elif (curr_time - end_pickup_time >= song_delay):
            buzzer.duty(512)
        
        if (curr_time - end_pickup_time >= (song_delay/2)):
            led.on()

        
        



    time.sleep(0.1)

