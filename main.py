import network
import socket
import time
import machine
from machine import Pin, PWM

# === Wi-Fi Setup ===
SSID = "your_wifi_name"
PASSWORD = "your_wifi_password"

# === Hardware Pins ===
light_pins = [1, 2, 3, 4, 5]         # Red lights
servo_pin = 6                        # Servo for flag
buzzer_pin = 7                       # Buzzer
wifi_led_pin = 9                     # Wi-Fi status LED
i = 0

# === Setup Outputs ===
lights = [Pin(pin, Pin.OUT) for pin in light_pins]
for item in light_pins:
    Pin(light_pins[i], Pin.OUT)
    i += 1
servo = PWM(Pin(servo_pin))
servo.freq(50)
buzzer = Pin(buzzer_pin, Pin.OUT)
wifi_led = Pin(wifi_led_pin, Pin.OUT)

# === Flag Waving State ===
flag_waving = False

# === Servo Control ===
def set_servo(angle):
    duty = int((angle / 180) * 2000 + 500)  # Maps 0-180 to 0.5ms–2.5ms
    servo.duty_u16(int(duty * 65535 / 20000))  # Convert to 16-bit

def wave_flag_once():
    for _ in range(4):
        set_servo(60)
        time.sleep(0.3)
        set_servo(120)
        time.sleep(0.3)

def raise_flag():
    set_servo(90)

def wave_flag_loop():
    global flag_waving
    while flag_waving:
        set_servo(60)
        time.sleep(0.3)
        set_servo(120)
        time.sleep(0.3)
    raise_flag()

# === Wi-Fi Connect ===
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)

    print("🔌 Connecting to Wi-Fi...")
    blink = True
    while not wlan.isconnected():
        wifi_led.value(blink)
        blink = not blink
        time.sleep(0.5)

    wifi_led.value(1)
    print("✅ Connected! IP:", wlan.ifconfig()[0])
    return wlan.ifconfig()[0]

# === Web Interface ===
html = """<!DOCTYPE html>
<html>
<head><title>F1 Race Control</title></head>
<body style="font-family:sans-serif;text-align:center;">
<h1>🚥 F1 Race Control</h1>
<form action="/start" method="get">
    <button style="font-size:24px;">Start Race</button>
</form><br>
<form action="/end" method="get">
    <button style="font-size:24px;">End Race</button>
</form><br>
<form action="/stop_flag" method="get">
    <button style="font-size:24px;">Stop Flag</button>
</form>
</body></html>
"""

def handle_client(conn):
    global flag_waving
    request = conn.recv(1024).decode()
    path = request.split(" ")[1]

    if path == "/start":
        print("🚦 Starting Race Sequence...")
        for light in lights:
            light.value(0)
            time.sleep(0.5)

        for light in lights:
            light.value(1)
        buzzer.value(1)
        time.sleep(0.3)
        buzzer.value(0)
        wave_flag_once()
        raise_flag()

    elif path == "/end":
        print("🏁 Waving Flag to End Race")
        flag_waving = True
        _thread.start_new_thread(wave_flag_loop, ())

    elif path == "/stop_flag":
        print("✋ Stopping Flag")
        flag_waving = False

    # Respond with webpage
    conn.send("HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n")
    conn.sendall(html)
    conn.close()

# === Main Program ===
ip = connect_wifi()
addr = socket.getaddrinfo(ip, 80)[0][-1]
s = socket.socket()
s.bind(addr)
s.listen(1)

print(f"🌍 Control panel ready at: http://{ip}")

raise_flag()  # Ensure flag is up

# === Web Server Loop ===
import _thread
while True:
    try:
        conn, addr = s.accept()
        handle_client(conn)
    except Exception as e:
        print("❌ Error:", e)
