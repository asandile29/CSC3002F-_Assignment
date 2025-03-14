#server
import socket
import time
import threading

#dictionary of peers available
#adress is key and fileName is value, which makes it easier to remove inactive peers, but harder to search for files

peers = {}
#lock the dictionary to avoid race conditions: synchronize access to peers
peersLock = threading.Lock()

#socket that seeder will connect to
seedSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
print("UDP Seeder Socket created successfully")

#reserve a port
port = 1111

#bind to the port
#no IP means the server is listening to requests from other computers on network
seedSocket.bind(('127.0.0.1', port))
print("socket binded to %s" %(port))

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
            break


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
            print(f"Peer {address} removed for file '{fileName}'")
            if not peers[fileName]:
                del peers[fileName]
                print(f"No more peers available for file '{fileName}'")
    


if __name__ == "__main__":
    try:
        sThread = threading.Thread(target=seederConnection, args=(seedSocket,))
        lThread = threading.Thread(target=leecherConnection, args=(leechSocket,))
            
        sThread.start()
        lThread.start()

        sThread.join()
        lThread.join()

    except KeyboardInterrupt:
        print("Server is shutting down")
    finally:
        seedSocket.close()
        leechSocket.close()
        print("Sockets closed.")

    