import socket

port = 50007;

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    s.bind(('', port))
    while True:
        data, addr = s.recvfrom(1024)
        print("UDP data from port {}: {}, addr: {}".format(port, data.decode(), addr))
