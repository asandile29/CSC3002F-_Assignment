leechSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
print("UDP Leecher Socket created successfully")

#reserve a port for leecher
port = 2222

#bind to the port
#no IP means the server is listening to requests from other computers on network
leechSocket.bind(('127.0.0.1', port))
print("socket binded to %s" %(port))

while True:
    #establish connection
    message, address = leechSocket.recvfrom(1024)
    print("Connection received from", address, ":", message.decode())
    fileName = message.decode().split()[1]
    if (message.decode().startswith('Request')):
            #send the list to leecher
            for peer in peers:
                fn = peer[1]
                ad = peer[0]
                if fn == fileName:
                    details = .(f"{ad} contains {fn}").encode()
                leechSocket.sendto(details, address)
                print("Response sent to ", address)
        