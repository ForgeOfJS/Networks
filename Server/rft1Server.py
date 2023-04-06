import socket, os, sys, random
from packet import *
from timer import *
from udt import *

seq = 0
ack = 1

HOST = "127.0.0.1"
PORT = int(input("Listen at Port#: "))
address = (HOST, PORT)

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server:
    while True:
        while True:
            # Get packets
            seqNum, data = extract(recv(server))

            if data == b'':
                continue

            pack = make(seqNum, b'ACK')
            send(pack)
            break

        seqNum, data = extract(recv(server))
        message = data.decode()
        # Check for CLOSE command and close connection if so.
        if message == 'CLOSE':
            print("Connection closed, See you later!")
            server.close()
            sys.exit()
        # Check for RETR command and perform operation if so, otherwise send nothing.
        if message[:4] == "RETR":
            message = message.split(" ")
            print(f"Asking for file {message[1]}")
            # Get file name and check in the predetermined file storage if file exists
            requestedFilePath = f'{os.getcwd()}\FileStorage\{message[1]}'
            # If file exists begin the transfer, otherwise send nothing.
            if os.path.isfile(requestedFilePath):
                with open(requestedFilePath, 'rb') as file:
                    print("Sending the file...")
                    # Open and read the file as bytes
                    fileContents = file.read()
                    fileBytes = bytes(fileContents)
                    fileSize = len(fileBytes)
                    packets = []
                    # Check if filesize is smaller than the largest packet byte size allowed
                    # If so, then add to packets and send to client.
                    if fileSize <= 1000:
                        packets.append(fileBytes)
                    else:
                        # Otherwise split file into 1000 bytes
                        # Find # of packets needed
                        numPackets = fileSize // 1000
                        # Segment file into 1000 bytes sized packets
                        for i in range(0, numPackets):
                            print()
                            start = i * 1000
                            end = start + 1000
                            packets.append(bytes(fileBytes[start:end]))
                        # Add last packet that covers the < 1000 bytes left over.
                        if fileSize % 1000 != 0:
                            packets.append(fileBytes[end:len(fileBytes)])

                    # TRANSMISSION
                    for i in range(len(packets)):
                        while seq != ack:
                            newPack = make(seq, packets[i])
                            # print(len(packets[i]))
                            send(newPack, server, address)
                            ack, data = extract(recv(server))
                        seq += 1

                    # Edge case, if packet is divisible by 1000 bytes, send "!" as EOF
                    if fileSize % 1000 == 0:
                        time.sleep(1)
                        send(b'!')
                    print("Transfer Complete!")
            else:
                print("File not found.")
                send(b'!')

        else:
            print("Command not recognized.")
            send(b'!')
