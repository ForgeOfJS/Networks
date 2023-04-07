import os, socket, sys, time
from packet import *
from timer import *
from udt import *

global seq, tferTime, packSent, packResent

seq = True
tferTime = Timer(-1)
packSent = 0
packResent = 0


def snwsend(sock, mess, addr):
    global seq, packSent
    dat = b''

    ack = not seq
    while seq != ack:
        newpack = make(seq, mess)
        print(f"{time.time()}: SENDING {mess}")
        send(newpack, sock, addr)
        packSent += 1
        if mess == b'ACK':
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


HOST = input("Provide Server IP: ")
PORT = int(input("Provide Port#: "))
address = (HOST, PORT)

# Look for and establish connection to server
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client.settimeout(5)
client.connect(address)

# Prompt user
clientRequest = input("RFTCli>")
clientRequestSeq = clientRequest.split(" ")

tferTime.start()
# Turn request into bytes and send request to server
snwsend(client, clientRequest.encode(), address)


# If client requests a CLOSE then client should exit
if clientRequest == "CLOSE":
    sys.exit()

# Begin the file transfer, i.e. create the file to have data placed into.
returnFilePath = f'{os.getcwd()}\FileStorage\copy_{clientRequestSeq[1]}'
file = open(returnFilePath, 'wb')

prevData = b''
# Start transferring packets
while True:
    # Get packets
    try:
        pack, address = recv(client)
        seqNum, data = extract(pack)
        seq = seqNum
    except socket.timeout:
        continue

    print(f"{time.time()}: RECEIVED {data}")


    if data == b'':
        print("EMPTY DATA")
        continue

    print(f"{time.time()}: SENDING ACK {seq}")
    snwsend(client, b'ACK', address)

    # Edge case, if command failed or file is divisible by 1000 bytes then stop file transfer
    if data == b'!':
        break

    # print(len(dat))
    if not prevData == data:
        file.write(data)
        prevData = data
    else:
        print(f"{time.time()}: DUPLICATE DATA. DISREGARDING.")

    # Once a non 1000 byte packet is received then stop the transfer.
    if len(data) != 1000:
        break
# File transfer is completed.
file.close()
print(f'Received {clientRequestSeq[1]} after {tferTime.stop()} seconds and {packSent} packets and {packResent} retransmits')
