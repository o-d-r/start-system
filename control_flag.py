import requests
import socket
import time

IP = "10.10.20.66"

def send_cmd(command):
    url = f"http://{IP}/startapi?{command}"
    try:
        response = requests.get(url, timeout=10)
        print(f"Sent: {command} | Status: {response.status_code}")
    except Exception as e:
        print(f"Failed to send: {command} | Error: {e}")

def main() -> None:
    last_cmd = None
    print("Keyboard Start Gate Control Started")
    print("S = Start\nI = Idle\nE = End")
    input = list(input().strip().lower())[0]
    if input != last_cmd:    
        if input == 's':
            send_cmd("cmd=start")
        elif input == 'i':
            send_cmd("cmd=idle")
        elif input == 'e':
            send_cmd("cmd=end")
        else:
            throw InputError
    last_cmd = input
    time.sleep(0.05)

if __name__ == "__main__":
    main()
