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
trackerSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
print("UDP Seeder Socket created successfully")

#reserve a port
port = 1111

#bind to the port
#no IP means the server is listening to requests from other computers on network
trackerSocket.bind(('127.0.0.1', port))
print("socket binded to %s" %(port))


def handleRequests(trackerSocket):
    while True:
        #establish connection
        try:
            message, address = trackerSocket.recvfrom(1024)
            print("Connection received from", address, ":", message.decode())
            fileName = message.decode().split()[1]

            #

            if (message.decode().startswith('Request')):
                    #send the list to leecher
                with peersLock:
                    if fileName in peers and peers[fileName]:
                        seederList = ",".join(f"{ip}:{port}" for ip, port in peers[fileName])
                        #send list of available peers with that particular file to leecher
                        trackerSocket.sendto(seederList.encode(), address)
                        print(f"Sent seeders {seederList} for file '{fileName}' to {address}")
                    else:
                        trackerSocket.sendto(b"", address)
                        print(f"No seeders available for '{fileName}' requested by {address}")

        
           
            #seeders
            elif (message.decode().startswith('Register')):
                with peersLock:
                    if fileName in peers:
                        if address not in peers[fileName]:
                            peers[fileName].append(address)
                    else:
                        peers[fileName] = [address]
                print(f"Registered seeder {address} for file '{fileName}'")

                try:
                    #send a ping to peers
                    trackerSocket.sendto(b'Hello', address)
                    trackerSocket.settimeout(5)
                    reply, _ = trackerSocket.recvfrom(1024)

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
                        trackerSocket.settimeout(None) #reset timeout for next peer
        except Exception as e:
            print(f"Error handling connection: {e}")
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
        thread1 = threading.Thread(target=handleRequests, args=(trackerSocket,))
        while True:
            pass
     
    except KeyboardInterrupt:
        print("Tracker server is shutting down")
    finally:
        trackerSocket.close()
        print("Socket is closed.")

    