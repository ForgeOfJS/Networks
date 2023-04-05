import socket, os, sys

print("Provide Server IP: ", end="")
HOST = input()
print("Provide Port#: ", end="")
PORT = int(input())

#Look for and establish connection to server
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))
print("You are now connected! Enter your commands now.")
#Prompt user
print("RFTCli>", end = " ")
clientRequest = input()
#Turn request into bytes and send request to server
message = bytes(clientRequest, 'utf-8')
clientRequestSeg = clientRequest.split(" ")
#Setup for GBN
gbnflag = False
expectedSeqNum = 0
#Setup for SBN
sbnflag = False
if len(clientRequestSeg) > 2:
    if clientRequestSeg[2] == "GBN":
        gbnflag = True
    elif clientRequestSeg[2] == "SBN":
        sbnflag = True
client.sendall(message)
#If client requests a CLOSE then client should exit
if clientRequest == "CLOSE": sys.exit()
#Begin the file transfer, i.e. create the file to have data placed into.
returnFilePath = f'{os.getcwd()}\FileStorage\copy_{clientRequestSeg[1]}'
file = open(returnFilePath, 'wb')
#Start transfering packets
while True:
    #Get packets
    data, address = client.recv(1024)
    #Edge case, if command failed or file is divisible by 1000 bytes then stop file transfer
    if data == b'!': break

    if gbnflag:
        #Go Back N Implementation
        seqNum = int(data[:3].decode())
        data = data[3:]
        #Verify seq #
        if seqNum == expectedSeqNum:
            ack = str(seqNum).encode()
            client.sendto(ack,address)
            print(f'Received packet {seqNum}, sent ACK {seqNum}')
            expectedSeqNum += 1
        else:
            print(f'Received out-of-order packet {seq_num}, waiting for {expected_seq_num}')


    print(len(data))
    file.write(data)
    #Once a non 1000 byte packet is recieved then stop the transfer. 
    if len(data) != 1000:
        break
#File transfer is completed.
file.close()
print(f'Recieved {clientRequestSeg[1]}')
