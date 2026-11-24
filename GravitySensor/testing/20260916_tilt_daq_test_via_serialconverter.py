import socket
import time

HOST = "10.10.10.71" # IP address of the serial converter
PORT = 32  # 実際のSLP2のポートに変更 (CH1: 23, CH2: 26, CH3: 29, CH4: 32)

s = socket.create_connection((HOST, PORT), timeout=3)
s.settimeout(5)

print(f"testing port {PORT}")
print("TCP connected")

# ASCII output mode
command = b"setoasc\r"
print("TX:", repr(command))
s.sendall(command)

try:
    data = s.recv(1024)
    print("RX after setoasc:", repr(data), "length:", len(data))
except socket.timeout:
    print("RX timeout after setoasc")

time.sleep(0.2)

# Angle request
command = b"get-x&y\r"
print("TX:", repr(command))

try:
    while True:
        try:
            
            s.sendall(command)

            data = s.recv(1024)

            print(
                "RX after get-x&y:",
                repr(data),
                "length:",
                len(data)
            )

            time.sleep(1)

        except socket.timeout:
            print("RX timeout after get-x&y")

except KeyboardInterrupt:
    print("\nStopped by Ctrl+C")

s.close()
