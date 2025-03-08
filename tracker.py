#server
import socket

#list of peers available
peers = []

for
#GeeksforGeeks Schools
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
print("UDP Socket created successfully")

#reserve a port
port = 1111

#bind to the port
#no IP means the server is listening to requests from other computers on network
serverSocket.bind(('127.0.0.1', port))
print("socket binded to %s" %(port))


while True:
    #establish connection
    message, addy = serverSocket.recvfrom(1024)
    print("Connection received from", addy, ":", message.decode())
    peers.append[addy]
    #send 'thank you' to client
    #encode to send byte type
    serverSocket.sendto("Thank you for connecting".encode(), addy)
    serverSocket.sentto(peers)
    print("Response sent to ", addy)
    #close client connection

    
