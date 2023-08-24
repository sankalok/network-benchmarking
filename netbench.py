#!/usr/bin/python

#Name: Sankalok Sen
#Development Platform: Locally using Windows (10) and Mac (13 Ventura) laptops acting as a Client and Server,
#   also have tested on academy11 and academy21.
#Python Version (Local): Python 3.11 & HKU (Server): Python 3.9

import sys
import socket
import time

PORT = 41351
DATA_SIZE_LARGE_PACKET = 10**6

def server(argv):
    #Port No. & IP Address (Hardcoded)
    port = PORT
    ip_address = '0.0.0.0'

    #Create Socket and Bind
    socket_server_TCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_server_TCP.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        socket_server_TCP.bind((ip_address, port))
    except socket.error as emsg:
        print("Socket Bind Error:", emsg)
        sys.exit(1)

    #Successful connection to Server
    print(f"Server is ready. Listening address: ({ip_address}, {port})")

    #Listen for new connection and accept
    socket_server_TCP.listen(5)
    try:
        conn, addr = socket_server_TCP.accept()
    except socket.error as emsg:
        print("Socket Accept Error:", emsg)
        sys.exit(1)

    #Create Socket and Bind for UDP
    socket_server_UDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    socket_server_UDP.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        socket_server_UDP.bind((ip_address, port))
    except socket.error as emsg:
        print("Socket Bind Error:", emsg)
        sys.exit(1)

    #Successful connection of client
    print(f"A client has connected and it is at: {addr}")

    #Test 1
    print()
    print("Start Test 1 - TCP - Large Transfer - 2 * 10**8 bytes")
    print()
    print("From Server to Client:")
    data = b'0' * DATA_SIZE_LARGE_PACKET
    start_time = time.perf_counter()
    for i in range(1, 201):
        conn.sendall(data)
        if(i % 10 == 0):
            print(f"{i * 100 / 200} % transferred")
    print()
    print(f"Sent Total: {200 * DATA_SIZE_LARGE_PACKET} bytes")
    #Receive 5 Byte Message
    data_received = conn.recv(5)
    if(len(data_received) == 5):
        print(f"Message received from Client to Server: {data_received.decode()}")
    end_time = time.perf_counter()
    print(f"Elapsed Time: {end_time - start_time} s")
    print(f"Throughput (from Server to Client): {200 / (end_time - start_time)} Mb/s")
    print()
    print("From Client to Server:")
    data_size_received = 0
    for i in range(1, 201):
        packet_data_received = b''
        while(len(packet_data_received) < 10**6):
            packet_data_received += conn.recv(10**6 - len(packet_data_received))
        data_size_received += len(packet_data_received)
    print(f"Received Total: {data_size_received} bytes")
    # Send 5 Byte Message
    data = b'DONE!'
    conn.sendall(data)

    #Test 2
    print()
    print("Start Test 2 - TCP - Small Transfer - 10000 bytes")
    print()
    print("From Server to Client:")
    data = b'0' * 10000
    start_time = time.perf_counter()
    conn.sendall(data)
    print(f"Sent Total: {len(data)} bytes")
    data_received = conn.recv(5)
    if(len(data_received) == 5):
        print(f"Message received from Client to Server: {data_received.decode()}")
    end_time = time.perf_counter()
    print(f"Elapsed Time: {end_time - start_time} s")
    print(f"Throughput (from Server to Client): {0.01 / (end_time - start_time)} Mb/s")
    print()
    print("From Client to Server:")
    data_received = b''
    while(len(data_received) < 10000):
     data_received += conn.recv(10000 - len(data_received))
    print(f"Received Total: {len(data_received)} bytes")
    # Send 5 Byte Message
    data = b'DONE!'
    conn.sendall(data)

    #Test 3
    print()
    print("Start Test 3 - UDP Pingpong - 5 bytes")
    print()
    print("From Server to Client:")
    data = b'5BYTE'
    total_time_client_RTT = 0.0
    for i in range(0, 5):
        start_time = time.perf_counter()
        socket_server_UDP.sendto(data, addr)
        data, address = socket_server_UDP.recvfrom(5)
        end_time = time.perf_counter()
        print(f"Reply from {addr}: time = {end_time - start_time} s")
        total_time_client_RTT += (end_time - start_time)

    print(f"Average RTT: {total_time_client_RTT/5} s")

    print()
    print("From Client to Server:")
    for i in range(0, 5):
        data, address = socket_server_UDP.recvfrom(5)
        socket_server_UDP.sendto(data, address)
        print(f"{(i+1)/5 * 100} % done")

    #Conclusion
    print()
    print("End of all benchmarks")
    socket_server_TCP.close()
    conn.close()
    socket_server_UDP.close()


def client(argv):
    #Port No. & IP Address
    port = PORT
    ip_address = argv[1]

    #Create Socket
    socket_client_TCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_client_TCP.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    #Dynammically Allocated Port (PORT = 0)
    socket_client_TCP.bind((socket.gethostname(), 0))

    #Connect to server
    try:
        socket_client_TCP.connect((ip_address, port))
    except socket.error as emsg:
        print("Socket Connect Error:", emsg)
        sys.exit(1)

    #Store TCP Port
    tcp_port = socket_client_TCP.getsockname()[1]

    #Create Socket and Connect (UDP)
    socket_client_UDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    socket_client_UDP.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    #Dynammically Update Port (USE SAME PORT AS TCP)
    socket_client_UDP.bind((socket.gethostname(), tcp_port))

    #Successful connection to Server
    print(f"Client has connected to server at: ({ip_address}, {port})")
    print(f"Client's address: {socket_client_TCP.getsockname()}")

    #Test 1
    print()
    print("Start Test 1 - TCP - Large Transfer - 2 * 10**8 bytes")
    print()
    print("From Server to Client:")
    data_size_received = 0
    for i in range(1, 201):
        packet_data_received = b''
        while(len(packet_data_received) < 10**6):
            packet_data_received += socket_client_TCP.recv(10**6 - len(packet_data_received))
        data_size_received += len(packet_data_received)
    print(f"Received Total: {data_size_received} bytes")
    # Send 5 Byte Message
    data = b'DONE!'
    socket_client_TCP.sendall(data)
    print()
    print("From Client to Server:")
    data = b'0' * DATA_SIZE_LARGE_PACKET
    start_time = time.perf_counter()
    for j in range(1, 201):
        socket_client_TCP.sendall(data)
        if(j % 10 == 0):
            print(f"{j * 100 / 200} % transferred")
    print()
    print(f"Sent Total: {200 * DATA_SIZE_LARGE_PACKET} bytes")
    #Receive 5 Byte Message
    data_received = socket_client_TCP.recv(5)
    if(len(data_received) == 5):
        print(f"Message received from Server to Client: {data_received.decode()}")
    end_time = time.perf_counter()
    print(f"Elapsed Time: {end_time - start_time} s")
    print(f"Throughput (from Client to Server): {200 / (end_time - start_time)} Mb/s")

    #Test 2
    print()
    print("Start Test 2 - TCP - Small Transfer - 10000 bytes")
    print()
    print("From Server to Client:")
    data_received = b''
    while(len(data_received) < 10000):
        data_received += socket_client_TCP.recv(10000 - len(data_received))
    print(f"Received Total: {len(data_received)} bytes")
    # Send 5 Byte Message
    data = b'DONE!'
    socket_client_TCP.sendall(data)
    print()
    print("From Client to Server:")    
    data = b'0' * 10000
    start_time = time.perf_counter()
    socket_client_TCP.sendall(data)
    print(f"Sent Total: {len(data)} bytes")
    data_received = socket_client_TCP.recv(5)
    if(len(data_received) == 5):
        print(f"Message received from Server to Client: {data_received.decode()}")
    end_time = time.perf_counter()
    print(f"Elapsed Time: {end_time - start_time} s")
    print(f"Throughput (from Client to Server): {0.01 / (end_time - start_time)} Mb/s")

    #Test 3
    print()
    print("Start Test 3 - UDP Pingpong - 5 bytes")
    print()
    print("From Server to Client:")
    for i in range(0, 5):
        data, address = socket_client_UDP.recvfrom(5)
        socket_client_UDP.sendto(data, address)
        print(f"{(i+1)/5 * 100} % done")
    print()
    print("From Client to Server:")
    data = b'5BYTE'
    total_time_server_RTT = 0.0
    for i in range(0, 5):
        start_time = time.perf_counter()
        socket_client_UDP.sendto(data, (ip_address, port))
        data, address = socket_client_UDP.recvfrom(5)
        end_time = time.perf_counter()
        print(f"Reply from ({ip_address}, {port}): time = {end_time - start_time} s")
        total_time_server_RTT += (end_time - start_time)
    print(f"Average RTT: {total_time_server_RTT/5} s")

    #Conclusion
    print()
    print("End of all benchmarks")
    socket_client_TCP.close()
    socket_client_UDP.close()

if __name__ == '__main__':
    if len(sys.argv) == 1:
        server(sys.argv)
    elif len(sys.argv) == 2:
        client(sys.argv)
    else:
        print('Usage [SERVER]: python|python3 netbench.py')
        print('Usage [CLIENT]: python|python3 netbench.py <hostname|ip-address>')
        sys.exit(1)
        