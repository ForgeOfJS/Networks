import socket, os, sys, random
from packet import *
from timer import *
from udt import *

global seq, packSent, packResent, tferTime

seq = True
packSent = 0
packResent = 0
tferTime = Timer(-1)


def snwsend(sock, mess, addr):
    global seq, packSent, packResent
    dat = b''

    ack = not seq
    while seq != ack:
        newpack = make(seq, mess)
        print(f"{time.time()}: SENDING {mess}")
        send(newpack, sock, addr)
        packSent += 1
        if mess == b'ACK' or mess == b'!':
            break
        print(f"{time.time()}: WAITING FOR ACK {seq}")
        try:
            packet, addr = recv(sock)
            ack, dat = extract(packet)
            print(f"{time.time()}: ACK {seq} RECEIVED")
        except socket.timeout:
            packResent += 1
            continue
    seq = not seq
    return dat


HOST = "127.0.0.1"
PORT = int(input("Listen at Port#: "))
address = (HOST, PORT)

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server:
    server.settimeout(5)
    server.bind(address)
    while True:
        while True:
            # Get packets
            try:
                pack, address = recv(server)
                seqNum, data = extract(pack)
            except socket.timeout:
                continue

            tferTime.start()
            print(f"{time.time()}: RECEIVED {data}")

            if data == b'':
                print("EMPTY DATA")
                continue

            print(f"{time.time()}: SENDING ACK {seq}")
            snwsend(server, b'ACK', address)
            break

        message = data.decode()
        # Check for CLOSE command and close connection if so.
        if message == 'CLOSE':
            print(f"{time.time()}: Connection closed, See you later!")
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
                    print("Sending the file...\n")
                    # Open and read the file as bytes
                    fileBytes = bytes(file.read())
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
                        if fileSize % 1000 != 0:
                            numPackets += 1
                        # Segment file into 1000 bytes sized packets
                        for i in range(numPackets):
                            start = i * 1000
                            end = (i+1) * 1000
                            if end > fileSize:
                                end = fileSize
                            packets.append(fileBytes[start:end])

                    # TRANSMISSION
                    try:
                        for i in range(len(packets)):
                            print(f"{time.time()}: SENDING PACKET {i}")
                            snwsend(server, packets[i], address)

                        # Edge case, if packet is divisible by 1000 bytes, send "!" as EOF
                        if fileSize % 1000 == 0:
                            snwsend(server, b'!', address)
                    except ConnectionResetError:
                        print("Connection Closed")
                    print(f"\nTransfer Complete after {tferTime.stop()} seconds.\nMinimum Packets Needed: {packSent-packResent}\nRetransmits: {packResent}\nTotal Packets Sent: {packSent}")
            else:
                print("File not found.")
                snwsend(server, b'!', address)

        else:
            print("Command not recognized.")
            snwsend(server, b'!', address)
