import socket, os, sys, time

#print("Provide Server IP: ", end="")
HOST = "127.0.0.1"#input()
#print("Provide Port#: ", end="")
PORT = 8000#int(input())
print("Provide Mode# (Type 'TCP' to skip UDP protocols): ", end="")
mode = input()

if mode == 'TCP':
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
    client.sendall(message)
    #If client requests a CLOSE then client should exit
    if clientRequest == "CLOSE": sys.exit()
    #Begin the file transfer, i.e. create the file to have data placed into.
    returnFilePath = f'{os.getcwd()}\FileStorage\copy_{clientRequestSeg[1]}'
    file = open(returnFilePath, 'wb')
    #Start transfering packets
    while True:
        #Get packets
        data = client.recv(1024)
        print(data.decode())
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
elif mode == "GBN":
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    serverAddress = (HOST, PORT)
    print("RFTCli>", end = " ")
    clientRequest = input()
    message = bytes(clientRequest, 'utf-8')
    clientRequestSeg = clientRequest.split(" ")
    client.sendto(message, serverAddress)
