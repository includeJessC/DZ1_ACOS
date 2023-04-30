#!/usr/bin/env python3
import json
import os
import socket
import socketserver

BUFFER_SIZE = 1024

# https://docs.python.org/3/library/socketserver.html
class MyUDPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        data = self.request[0].strip()
        sock = self.request[1]
        data = (data.decode()).split()
        host = data[1].upper()
        port = int(os.environ['PORT'])
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect((host, port))
            s.sendto(str.encode(""), (host, port))
            data_response, server = s.recvfrom(BUFFER_SIZE)
            data_response = json.loads(data_response.decode())
            print(data_response)
            result_ = f'{data_response["format"]} - {data_response["s_time"] * 1000}ms - {data_response["serial_size"]} - {data_response["d_time"] * 1000}ms\n'
        sock.sendto(str.encode(result_), self.client_address)


if __name__ == "__main__":
    with socketserver.UDPServer(("0.0.0.0", 2000), MyUDPHandler) as server:
        server.serve_forever()
