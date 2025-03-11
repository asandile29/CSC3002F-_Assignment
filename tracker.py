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
portL = 2222

#bind to the port
#no IP means the server is listening to requests from other computers on network
leechSocket.bind(('127.0.0.1', portL))
print("socket binded to %s" %(portL))

def leecherConnection(leechSocket):
    while True:
        #establish connection
        messageL, addyL = leechSocket.recvfrom(1024)
        print("Connection received from", addyL, ":", messageL.decode())
        try:
            fileName = messageL.decode().split()[1]

            if (messageL.decode().startswith('Request')):
                    #send the list to leecher
                with peersLock:
                    if fileName in peers:
                        seederList = ",".join(f"{ip}:{port}" for ip, port in peers[fileName])
                        #send list of available peers with that particular file to leecher
                        leechSocket.sendto(seederList.encode(), addyL)
                        print(f"Sent seeders {seederList} for file '{fileName}' to {addyL}")
                    else:
                        leechSocket.sendto(b"", addyL)
                        print(f"No seeders available for '{fileName}' requested by {addyL}")

        except Exception as e:
            print(f"Error handling leecher connection: {e}")


def seederConnection(seedSocket):
    while True:
        #establish connection
        messageS, addy = seedSocket.recvfrom(1024)
        print("Connection received from", addy, ":", messageS.decode())
        try:
            fileName = messageS.decode().split()[1]

            #fileName = messageS.decode().split()[1]
            #review the messageS sent from user
            #seeders
            if (messageS.decode().startswith('Register')):
                if fileName in peers:
                    with peersLock:
                        if addy not in peers[fileName]:
                            peers[fileName].append(addy)
                else:
                    peers[fileName] = [addy]
                print(f"Registered seeder {addy} for file '{fileName}'")


                #send a ping to peers
                seedSocket.sendto(b'Hello', addy)
                seedSocket.settimeout(5)
                try:
                    reply, _ = seedSocket.recvfrom(1024)

                    #check if peer is active
                    if reply == b'ALIVE':
                        print("Peer", addy, "is active")
                    else:
                        print("Peer", addy, "is inactive. The peer has been removed.")
                        with peersLock:
                            if fileName in peers and addy in peers[fileName]:
                                #remove inactive peer from list
                                peers[fileName].remove(addy)
                                if not peers[fileName]:
                                    del peers[fileName]

                        
                except socket.timeout: 
                    #remove unresponsive peer
                    print("Peer ", addy," did not respond. The peer has been removed")
                    with peersLock:
                        if fileName in peers and addy in peers[fileName]:
                            peers[fileName].remove(addy)
                            if not peers[fileName]:
                                del peers[fileName]
                finally:
                    seedSocket.settimeout(None)
        except:



sThread = threading.Thread(target=seederConnection, args=(seedSocket,))
lThread = threading.Thread(target=leecherConnection, args=(leechSocket,))
    
sThread.start()
lThread.start()

sThread.join()
lThread.join()

   