"""
EXPECTED HTTP FORMAT: GET /startapi?cmd=idle
valid cmd = idle, end, start
"""
import network
import socket
import time
import machine
from machine import Pin, PWM

# === Wi-Fi Setup ===
SSID = "IoT"
PASSWORD = "launchRob0t$"

LIGHT1_PIN = 1
LIGHT2_PIN = 2
LIGHT3_PIN = 3
LIGHT4_PIN = 4
LIGHT5_PIN = 5
SERVO_PIN = 6
BUZZER_PIN = 7
LED = 9

# === Setup Outputs ===
light1 = Pin(LIGHT1_PIN)
light2 = Pin(LIGHT2_PIN)
servo = PWM(Pin(SERVO_PIN))
servo.freq(50)
buzzer = Pin(BUZZER_PIN, Pin.OUT)
wifi_led = Pin(LED, Pin.OUT)

# === Flag Waving State ===
flag_waving = False

class Flag:
    
    def set(angle):
        duty = int((angle / 180) * 2000 + 500)  # Maps 0-180 to 0.5ms–2.5ms
        servo.duty_u16(int(duty * 65535 / 20000))  # Convert to 16-bit
    
    def wave(self):
        self.set(60)
        time.sleep(0.3)
        self.set(120)
        time.sleep(0.3)
        self.set(90)
    
    def wave_repeated(self):
        global flag_waving
        while flag_waving:
            self.set(60)
            time.sleep(0.3)
            self.set(120)
            time.sleep(0.3)
        self.set(90)
        
    def start_race(self):
        """
        F1 Starting Lights with buzzer every light, wave flag repeatedly for 5 seconds.
        """
        global LIGHT1_PIN
        global LIGHT2_PIN
        global LIGHT3_PIN
        global LIGHT4_PIN
        global LIGHT5_PIN
        global flag_waving
        
        LIGHT1_PIN.off()
        buzzer.on()
        time.sleep(0.5)
        buzzer.off()
        time.sleep(0.5)
        
        LIGHT2_PIN.off()
        buzzer.on()
        time.sleep(0.5)
        buzzer.off()
        time.sleep(0.5)
        
        LIGHT3PIN.off()
        buzzer.on()
        time.sleep(0.5)
        buzzer.off()
        time.sleep(0.5)
        
        LIGHT4_PIN.off()
        buzzer.on()
        time.sleep(0.5)
        buzzer.off()
        time.sleep(0.5)
        
        LIGHT5_PIN.off()
        buzzer.on()
        time.sleep(0.5)
        buzzer.off
        time.sleep(random.uniform(0.2, 3.0))
        
        LIGHT1_PIN.on()
        LIGHT2_PIN.on()
        LIGHT3_PIN.on()
        LIGHT4_PIN.on()
        LIGHT5_PIN.on()
        flag_waving = True
        self.wave_repeated()
        buzzer.on()
        time.sleep(1)
        buzzer.off()
    
    def end_race(self):
        self.wave_repeated()
        buzzer.on()
        
    def idle(self):
        global flag_waving
        flag_waving = False
        buzzer.off()
        LIGHT1_PIN.on()
        LIGHT2_PIN.on()
        LIGHT3_PIN.on()
        LIGHT4_PIN.on()
        LIGHT5_PIN.on()

# === Wi-Fi Connect ===
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)

    print("Connecting to Wi-Fi...")
    blink = True
    while not wlan.isconnected():
        wifi_led.toggle(blink)
        time.sleep(0.5)

    wifi_led.value(1)
    print("Connected! IP:", wlan.ifconfig()[0])
    return wlan.ifconfig()[0]

def parse_request(request, flag: Flag):
    cmd = split(request, "=")[1]
    cmd_char = list(cmd)[0]
    
    if cmd_char == 'i':
        Flag.idle()
        return
    
    elif cmd_char == 's':
        Flag.start_race()
        return
    
    elif cmd_char == 'e':
        Flag.end_race()
        return

def main():
    Flag = Flag
    ip = connect_wifi()
    addr = socket.getaddrinfo(ip, 80)[0][-1]
    s = socket.socket()
    s.bind(addr)
    s.listen(1)
    Flag.set(90)
    
    # === Web Server Loop ===
    while True:
        cl, addr = sock.accept()
        try:
            request = cl.recv(1024).decode()
            print("Request received:")
            print(request)
            if 'GET /startapi?' in request:
                parse_request(request, Flag)
                cl.send("HTTP/1.1 204 No Content\r\n\r\n")
            else:
                cl.send("HTTP/1.1 404 Not Found\r\n\r\n")
        except Exception as e:
            print("Request error:", e)
        finally:
            cl.close()

