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
light3 = Pin(LIGHT3_PIN)
light4 = Pin(LIGHT4_PIN)
light5 = Pin(LIGHT5_PIN)
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
        global flag_waving
        
        light1.off()
        buzzer.on()
        time.sleep(0.5)
        buzzer.off()
        time.sleep(0.5)
        
        light2.off()
        buzzer.on()
        time.sleep(0.5)
        buzzer.off()
        time.sleep(0.5)
        
        light3.off()
        buzzer.on()
        time.sleep(0.5)
        buzzer.off()
        time.sleep(0.5)
        
        light4.off()
        buzzer.on()
        time.sleep(0.5)
        buzzer.off()
        time.sleep(0.5)
        
        light5.off()
        buzzer.on()
        time.sleep(0.5)
        buzzer.off
        time.sleep(random.uniform(0.2, 3.0))
        
        light1.on()
        light2.on()
        light3.on()
        light4.on()
        light5.on()
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
        light1.on()
        light2.on()
        light3.on()
        light4.on()
        light5.on()

# === Wi-Fi Connect ===
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)

    print("Connecting to Wi-Fi...")
    while not wlan.isconnected():
        wifi_led.toggle()
        time.sleep(0.5)

    wifi_led.value(1)
    print("Connected! IP:", wlan.ifconfig()[0])
    return wlan.ifconfig()[0]

def parse_request(request, flag: Flag):
    flag = Flag()
    cmd = request.split("=")[1]
    cmd_char = list(cmd)[0]
    
    if cmd_char == 'i':
        print("Idling...")
        flag.idle()
        return
    
    elif cmd_char == 's':
        print("Starting race...")
        flag.start_race()
        return
    
    elif cmd_char == 'e':
        print("Ending race...")
        flag.end_race()
        return

def main():
    Gate = Flag
    ip = connect_wifi()
    addr = socket.getaddrinfo(ip, 80)[0][-1]
    s = socket.socket()
    s.bind(addr)
    s.listen(1)
    Gate.set(90)
    
    # === Web Server Loop ===
    while True:
        cl, addr = s.accept()
        request = cl.recv(1024).decode("utf-8")
        print("Request received:")
        print(request)
        if 'GET /startapi?' in request:
            parse_request(request, Gate)
            cl.send("HTTP/1.1 204 No Content\r\n\r\n")
        else:
            cl.send("HTTP/1.1 404 Not Found\r\n\r\n")
        cl.close()
main()

