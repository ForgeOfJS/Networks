import socket, os, sys, random
DROP_PROB = 2

# Creates a packet from a sequence number and byte data
def make(seq_num, data = b''):
    seq_bytes = seq_num.to_bytes(4, byteorder = 'little', signed = True)
    return seq_bytes + data

# Creates an empty packet
def make_empty():
    return b''

# Extracts sequence number and data from a non-empty packet
def extract(packet):
    seq_num = int.from_bytes(packet[0:4], byteorder = 'little', signed = True)
    return seq_num, packet[4:]


# Send a packet across the unreliable channel
# Packet may be lost
def send(packet, sock, addr):
    if random.randint(0, 10) > DROP_PROB:
        sock.sendto(packet, addr)
    return

# Receive a packet from the unreliable channel
def recv(sock):
    packet, addr = sock.recvfrom(1024)
    return packet, addr

print("Provide Server IP: ", end="")
HOST = input()
print("Provide Port#: ", end="")
PORT = int(input())
address = (HOST, PORT)

#Look for and establish connection to server
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
print("You are now connected! Enter your commands now.")

#Prompt user
print("RFTCli>", end = " ")
clientRequest = input()

#Turn request into bytes and send request to server
message = bytes(clientRequest, 'utf-8')
clientRequestSeg = clientRequest.split(" ")
client.sendall(message)

#If client requests a CLOSE then client should exit
if clientRequest == "CLOSE": sys.exit()

#Begin the file transfer, i.e. create the file to have data placed into.
returnFilePath = f'{os.getcwd()}\FileStorage\copy_{clientRequestSeg[1]}'
file = open(returnFilePath, 'wb')
#Start transfering packets
while True:
    #Get packets
    data = recv(client)
    #Edge case, if command failed or file is divisible by 1000 bytes then stop file transfer
    if data == b'!': break
    print(len(data))
    file.write(data)
    #Once a non 1000 byte packet is recieved then stop the transfer. 
    if len(data) != 1000:
        break
#File transfer is completed.
file.close()
print(f'Recieved {clientRequestSeg[1]}')
