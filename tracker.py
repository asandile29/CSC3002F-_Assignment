#server
import socket

#list of peers available


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
    #send 'thank you' to client
    #encode to send byte type
    serverSocket.sendto("Thank you for connecting".encode(), addy)
    print("Response sent to ", addy)
    #close client connection

    
