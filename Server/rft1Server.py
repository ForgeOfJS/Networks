import socket, sys, os, time

HOST = "127.0.0.1"
print("Listen at Port#: ", end="")
PORT = int(input())

#Start server and listen for a connection.
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
    server.bind((HOST, PORT))
    server.listen()
    print(f'Listening for connection at {PORT}...')
    while True:
        #Connection is established.
        conn, addr = server.accept()
        print(f"Connection accepted from {addr}.")
        data = conn.recv(1024)
        message = data.decode()
        #Check for CLOSE command and close connection if so.
        if message == 'CLOSE':
            print("Connection closed, See you later!")
            conn.close()
            sys.exit()
        #Check for RETR command and perform opearation if so, otherwise send nothing.
        if message[:4] == "RETR":
            message = message.split(" ")
            print(f"Asking for file {message[1]}")
            #Get file name and check in the predetermined file storage if file exists
            requestedFilePath = f'{os.getcwd()}\FileStorage\{message[1]}'
            #If file exists begin the transfer, otherwise send nothing.
            if os.path.isfile(requestedFilePath):
                with open(requestedFilePath, 'rb') as file:
                    print("Sending the file...")
                    #Open and read the file as bytes
                    fileContents = file.read()
                    fileBytes = bytes(fileContents)
                    fileSize = len(fileBytes)
                    packets = []
                    #Check if filesize is smaller than largest packet byte size allowed
                    #If so, then add to packets and send to client.
                    if fileSize <= 1000:
                        packets.append(fileBytes)
                    else:
                        #Otherwise split file into 1000 bytes
                        #Find # of packets needed
                        numPackets = fileSize // 1000
                        #Segment file into 1000 bytes sized packets
                        for i in range(0, numPackets):
                            print()
                            start = i * 1000
                            end = start + 1000
                            packets.append(bytes(fileBytes[start:end]))
                        #Add last packet that covers the < 1000 bytes left over.
                        if fileSize % 1000 != 0: packets.append(fileBytes[end:len(fileBytes)])
                    #Send the packets back to back
                    if len(message) == 3:
                        if message[2] == "GBN":
                            #Go Back N
                            window_size = 4
                            timeout = 5.0
                            seq_num = 0
                            expected_ack = 0
                            window_start = 0
                            window_end = window_size - 1

                            # Send initial window of packets
                            for i in range(window_size):
                                packet = f'{seq_num:03d}'.encode() + packets[seq_num]
                                server.sendto(packet, (HOST, PORT))
                                print(f'Sent packet {seq_num}')
                                seq_num += 1

                            # Start timer
                            start_time = time.time()

                            while expected_ack < len(packets):
                                # Wait for ACK or timeout
                                server.settimeout(timeout - (time.time() - start_time))
                                try:
                                    data, address = server.recvfrom(4096)
                                except socket.timeout:
                                    # Timeout occurred, resend packets in window
                                    print('Timeout, resending packets')
                                    for i in range(window_start, window_end+1):
                                        packet = f'{i:03d}'.encode() + packets[i]
                                        server.sendto(packet, (HOST, PORT))
                                        print(f'Resent packet {i}')
                                    start_time = time.time()
                                    continue
                                
                                # Parse ACK
                                ack_num = int(data.decode())
                                print(f'Received ACK {ack_num}')
                                
                                # Check if ACK is in window
                                if ack_num < window_start or ack_num > window_end:
                                    # Ignore out-of-window ACK
                                    continue
                                
                                # Update expected ACK number and window boundaries
                                expected_ack = ack_num + 1
                                window_start = ack_num + 1
                                window_end = min(window_start + window_size - 1, len(packets) - 1)
                                
                                # Send next packets in window
                                for i in range(window_start, window_end+1):
                                    packet = f'{i:03d}'.encode() + packets[i]
                                    server.sendto(packet, (HOST, PORT))
                                    print(f'Sent packet {i}')
                                
                                # Restart timer
                                start_time = time.time()
                            if fileSize % 1000 == 0:
                                time.sleep(1)
                                conn.send(b'!')
                            print("Transfer Complete!")

                    else:
                        for packet in packets:
                            print(len(packet))
                            conn.send(packet)
                        #Edge case, if packet is divisble by 1000 bytes, send "!" as EOF
                        if fileSize % 1000 == 0:
                            time.sleep(1)
                            conn.send(b'!')
                        print("Transfer Complete!")
            else:
                print("File not found.")
                conn.send(b'!')

        else:
            print("Command not recongnized.")
            conn.send(b'!')