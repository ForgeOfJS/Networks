import socket, sys, os, time;
import customTimer, packet, udt

HOST = "127.0.0.1"
#print("Listen at Port#: ", end="")
PORT = 8000 #int(input())
print("Provide Mode# (Type 'TCP' to skip UDP protocols): ", end="")
mode = "GBN"#input() 

if mode == "TCP":
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
                                packets.append(bytearray(fileBytes[start:end]))
                            #Add last packet that covers the < 1000 bytes left over.
                            if fileSize % 1000 != 0: packets.append(fileBytes[end:len(fileBytes)])
                        #Send the packets back to back
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
elif mode == "GBN":
    #UDP Socket
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    serverAddress = (HOST,PORT)
    #Set up GBN window and ack
    seqNum = 0
    expectedAck = 0
    windowStart = 0
    windowSize = 5
    windowEnd = windowSize - 1
    server.bind(serverAddress)
    print(f"Server listening on {PORT}...")
    data, addr = udt.recv(server)
    print(f'Recieved message from {addr}')
    message = data.decode()
    if message == 'CLOSE':
        print("Connection closed, See you later!")
        server.close()
        sys.exit()
    if message[:4] == "RETR":
        message = message.split(" ")
        requestedFilePath = f'{os.getcwd()}\FileStorage\{message[1]}'
        packets = []
        if os.path.isfile(requestedFilePath):
            with open(requestedFilePath, 'rb') as file:
                print("Sending the file...")
                fileContents = file.read()
                fileBytes = bytes(fileContents)
                fileSize = len(fileBytes)
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
                        packets.append(bytearray(fileBytes[start:end]))
                    #Add last packet that covers the < 1000 bytes left over.
                    if fileSize % 1000 != 0: packets.append(fileBytes[end:len(fileBytes)])
            #Send file using the GBN protocol
            #Establish window
            server.settimeout(5)
            for i in range(windowStart, windowEnd):
                if i < len(packets):
                    print(f'Sending packet{i} with seqNum {i}')
                    packetToSend = packet.make(i, packets[i])
                    udt.send(packetToSend, server, addr)
            #Redundancy for first window, it works tho
            #TODO: deal with redundancy and dont break the trasnmission
            while expectedAck < len(packets):
                try:
                    print('Recieving ack...')
                    ack, addr = udt.recv(server)
                except socket.timeout:
                    print("Timer ran out, resending window.")
                    for i in range(windowStart, windowEnd):
                        print(f'Sending packet{i} with seqNum {i}')
                        packetToSend = packet.make(i, packets[i])
                        udt.send(packetToSend, server, addr)
                    packetTimer = customTimer.Timer(10)
                    continue
            
                ackNum = int(ack.decode())

                if ackNum < windowStart or ackNum > windowEnd:
                    print('Invalid Ack, ignoring...')
                    continue
                expectedAck += 1
                windowStart += 1
                windowEnd += 1

                #Send any packets not send in new window
                for i in range(windowStart, windowEnd):
                    if i == expectedAck and i < len(packets):
                        print(f'Sending packet{i} with seqNum {i}')
                        packetToSend = packet.make(i, packets[i])
                        udt.send(packetToSend, server, addr)
                packetTimer = customTimer.Timer(10)
            print("Transfer Complete!")
        else:
            print("File not found.")
            udt.send(b'!', server, addr)
    else:
        print("Command not recongnized.")
        udt.send(b'!', server, addr)
        
            

