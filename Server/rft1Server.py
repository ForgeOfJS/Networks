import socket, sys, os, time

def snwReceive(sock):

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