#server
import socket
import time
import threading

#dictionary of peers available
#adress is key and fileName is value, which makes it easier to remove inactive peers, but harder to search for files

peers = {}
#lock the dictionary to avoid race conditions: synchronize access to peers
peersLock = threading.Lock()


def leecherConnection(s, fileName, address):
    while True:
        
        try:
            
                with peersLock:
                    if fileName in peers:
                        seederList = ",".join(f"{ip}:{port}" for ip, port in peers[fileName])
                        #send list of available peers with that particular file to leecher
                        s.sendto(seederList.encode(), address)
                        print(f"Sent seeders {seederList} for file '{fileName}' to {address}")
                    else:
                        s.sendto(b"", address)
                        print(f"No seeders available for '{fileName}' requested by {address}")

        except Exception as e:
            print(f"Error handling leecher connection: {e}")
       # finally:
           # s.close();


def seederConnection(s, fileName, address):
    while True:
        try:
            with peersLock:
                if fileName in peers:
                    if address not in peers[fileName]:
                        peers[fileName].append(address)
                else:
                    peers[fileName] = [address]
            print(f"Registered seeder {address} for file '{fileName}'")

            try:
                #send a ping to peers
                s.sendto(b'Hello', address)
                s.settimeout(5)
                reply, _ = s.recvfrom(1024)

                #check if peer is active
                if reply == b'ALIVE':
                    print("Peer", address, "is active")
                else:
                    print("Peer", address, "is inactive. The peer has been removed.")
                    removePeer(fileName, address)

                            
            except socket.timeout: 
                #remove unresponsive peer
                print("Peer ", address," did not respond. The peer has been removed")
                removePeer(fileName, address)
            finally:
                    s.settimeout(None) #reset timeout for next peer
        except Exception as e:
            print(f"Error handling seeder connection: {e}")
        #finally:
         #   s.close();

def removePeer(fileName, address):
    with peersLock:
        if fileName in peers and address in peers[fileName]:
            peers[fileName].remove(address)
            if not peers[fileName]:
                del peers[fileName]
    


if __name__ == "__main__":
    #socket that seeder will connect to
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print("UDP Socket created successfully")

    #reserve a port
    port = 1111

    #bind to the port
    #no IP means the server is listening to requests from other computers on network
    s.bind(('127.0.0.1', port))
    print("socket binded to %s" %(port))

    message, address = s.recvfrom(1024)
    print("Connection received from", address, ":", message.decode())
    fileName = message.decode().split()[1]

    if (message.decode().startswith('Register')):
        sThread = threading.Thread(target=seederConnection, args=(s, fileName, address))
        sThread.start()

    elif (message.decode().startswith('Request')):
        lThread = threading.Thread(target=leecherConnection, args=(s, fileName, address))
        lThread.start()

    else:
        s.sendto("Incorrect message format")
        

    sThread.join()
    lThread.join()

#server
import socket
import time
import threading

#dictionary of peers available
#adress is key and fileName is value, which makes it easier to remove inactive peers, but harder to search for files

peers = {}
#lock the dictionary to avoid race conditions: synchronize access to peers
peersLock = threading.Lock()

#GeeksforGeeks Schools
#socket that seeder will connect to
seedSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
print("UDP Seeder Socket created successfully")

#reserve a port
portS = 1111

#bind to the port
#no IP means the server is listening to requests from other computers on network
seedSocket.bind(('127.0.0.1', portS))
print("socket binded to %s" %(portS))

#make socket that leecher will connect to
leechSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
print("UDP Leecher Socket created successfully")

#reserve a port for leecher
port = 2222

#bind to the port
#no IP means the server is listening to requests from other computers on network
leechSocket.bind(('127.0.0.1', port))
print("socket binded to %s" %(port))

def leecherConnection(leechSocket):
    while True:
        #establish connection
        message, addressL = leechSocket.recvfrom(1024)
        print("Connection received from", addressL, ":", message.decode())
        try:
            fileName = message.decode().split()[1]

            if (message.decode().startswith('Request')):
                    #send the list to leecher
                with peersLock:
                    if fileName in peers:
                        seederList = ",".join(f"{ip}:{port}" for ip, port in peers[fileName])
                        #send list of available peers with that particular file to leecher
                        leechSocket.sendto(seederList.encode(), addressL)
                        print(f"Sent seeders {seederList} for file '{fileName}' to {addressL}")
                    else:
                        leechSocket.sendto(b"", addressL)
                        print(f"No seeders available for '{fileName}' requested by {addressL}")

        except Exception as e:
            print(f"Error handling leecher connection: {e}")


def seederConnection(seedSocket):
    while True:
        try:
            #establish connection
            message, address = seedSocket.recvfrom(1024)
            print("Connection received from", address, ":", message.decode())
            fileName = message.decode().split()[1]

            #review the message sent from user
            #seeders
            if (message.decode().startswith('Register')):
                with peersLock:
                    if fileName in peers:
                        if address not in peers[fileName]:
                            peers[fileName].append(address)
                    else:
                        peers[fileName] = [address]
                print(f"Registered seeder {address} for file '{fileName}'")

                try:
                    #send a ping to peers
                    seedSocket.sendto(b'Hello', address)
                    seedSocket.settimeout(5)
                    reply, _ = seedSocket.recvfrom(1024)

                    #check if peer is active
                    if reply == b'ALIVE':
                        print("Peer", address, "is active")
                    else:
                        print("Peer", address, "is inactive. The peer has been removed.")
                        removePeer(fileName, address)

                            
                except socket.timeout: 
                    #remove unresponsive peer
                    print("Peer ", address," did not respond. The peer has been removed")
                    removePeer(fileName, address)
                finally:
                        seedSocket.settimeout(None) #reset timeout for next peer
        except Exception as e:
            print(f"Error handling seeder connection: {e}")
            break

def removePeer(fileName, address):
    with peersLock:
        if fileName in peers and address in peers[fileName]:
            peers[fileName].remove(address)
            if not peers[fileName]:
                del peers[fileName]
    


if __name__ == "__main__":
    try:
        sThread = threading.Thread(target=seederConnection, args=(seedSocket,))
        lThread = threading.Thread(target=leecherConnection, args=(leechSocket,))
        
        sThread.start()
        lThread.start()

        sThread.join()
        lThread.join()

    except KeyboardInterrupt:
        print("Sedrver is shutting down")
    finally:
        seedSocket.close()
        leechSocket.close()
        print("Sockets closed")

    