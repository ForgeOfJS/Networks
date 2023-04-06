import os, random, socket, sys
from packet import *
from timer import *
from udt import *


print("Provide Server IP: ", end="")
HOST = input()
print("Provide Port#: ", end="")
PORT = int(input())
address = (HOST, PORT)

# Look for and establish connection to server
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
print("You are now connected! Enter your commands now.")

# Prompt user
print("RFTCli>", end=" ")
clientRequest = input().split(" ")

# Turn request into bytes and send request to server
message = make(1, clientRequest)
send(message, client, address)

# If client requests a CLOSE then client should exit
if clientRequest == "CLOSE":
    sys.exit()

# Begin the file transfer, i.e. create the file to have data placed into.
returnFilePath = f'{os.getcwd()}\FileStorage\copy_{clientRequest[1]}'
file = open(returnFilePath, 'wb')
# Start transferring packets
while True:
    # Get packets
    dat = recv(client)
    seqNum, dat = extract(dat)
    if dat == b'':
        continue

    # Edge case, if command failed or file is divisible by 1000 bytes then stop file transfer
    if dat == b'!':
        break
    print(len(dat))
    file.write(dat)
    # Once a non 1000 byte packet is recieved then stop the transfer.
    if len(dat) != 1000:
        break
# File transfer is completed.
file.close()
print(f'Received {clientRequest[1]}')
