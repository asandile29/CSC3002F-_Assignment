#Responsibilities:
    #Divide the file into chunks: The file is split into fixed-size parts (e.g., 512 KB).
    #Register with the tracker: The seeder informs the tracker that it is available and 
    #specifies which file it has.
    # Respond to leecher requests: When a leecher requests a chunk, the seeder 
    #transfers it using TCP.
    # Use TCP for reliable data transfer: Since TCP ensures the correct order of data 
    #and retransmits lost packets, it is used for file transfer.
    # Periodically notify the tracker of its availability: This helps leechers find available 
    #sources.
import socket
import threading
import time
import os

class Seeder:
    

#file_path (str) – Path to the file to be shared.
#chunks (dict) – Stores file chunks {chunk_id: chunk_data}.
#tracker_ip (str) – IP address of the tracker.
#tracker_port (int) – Tracker’s UDP port.


    def __init__(self, file_name: str, tracker_IP: str, tracker_port: int, 
               seeder_IP:str, seeder_port:int, Checkin_Interval:str):

               self.file_name = file_name
               self.chunks = {}
               self.tracker_IP = tracker_IP
               self.tracker_port = tracker_port
               self.seeder_IP = seeder_IP
               self.seeder_port = seeder_port
               self.Checkin_Interval = Checkin_Interval
               
    

    
    def inform_Tracker(self):
          with socket.socket(socket.AF_INET,socket.SOCK_DGRAM) as UDP_sock: # create a udp socket
                message = f"REGISTER {self.file_name} {self.seeder_IP}{self.seeder_port}"
                UDP_sock.sendto(message.encode(),self.tracker_port) # send the above message to the tracker to show availability
                print(f"Registered with the tracker for the file: {self.file_name}")
                UDP_sock.close()         
          


    def start_Server(self):
          
          try:
                  #create a tcp socket
                  TCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                  # bind to all available interfaces and a specified port
                  TCP.bind(("0.0.0.0", self.seeder_port))
                  #listen for incoming connections
                  TCP.listen()
                  print(f"Listening to connections from port:{self.seeder_port}...")

                  #we want to keep listening for connections
                  while True:
                        client_socket, client_address = TCP.accept()#accept leecher connection
                        print(f"Leecher {client_address} connected.")
                        #start new thread to handle the client
                        Client_thread = threading.Thread(target= self.Attend_clients(), args = (client_socket,client_address))
                        #Client_thread.daemon = True
                        Client_thread.start()

          except Exception as e:
                print(f"Error: {e}")
              
          finally:
                TCP.close() 

    def Attend_clients(self, client_socket, client_address) :
          try:
                while True:
                      #receive and print client messages
                      request = client_socket.recv(1024).decode("utf-8")
                      # if request is empty or client requests to close connection
                      #then seeder responds with closed and connection breaks
                      if not request or request.lower == "close":
                            client_socket.send("closed".encode("utf-8"))
                            break
                      print(f"Received: {request}")
                      # send response to client
                      client_socket.send("Accepted".encode("utf-8"))
                       #begin sending files if request is a file_name(*are we sure the client will always request a 
                       #filename or will there be different instances sometimes and do i need to accomodate that?)
                      if request:
                            self.Send_files(request, client_socket)
                      else:
                            #respond to client
                            client_socket.send("Accepted".encode("utf-8"))      
                            
          except Exception as e:
                print(f"Error occured while attending to client: {e}") 
          finally:
                client_socket.close()
                print(f"Connection to client ({client_address[0]:{client_address[1]}}) closed!") 


    def Send_files(self, file_name, client_socket):
          #sending the file chunks to the leecher
          try:
                with open(self.file_name, "rb") as file:
                      while True:
                            chunk = file.read(1024)# read 1024 bytes at a time(will this ever compromise transfer time if we have a larger file?)
                            if not chunk:
                                  break # stop sending chunks if file is transfer is complete
                            client_socket.send(chunk) #send chunk to client
                            print(f"Sent {len(chunk)} bytes to leecher.")
                print(f"File transfer complete!")
          # if file is not found then show error(should i prompt client to try sending file again?)
          except FileNotFoundError:
                
                error_message = "Error: File not found!"
                client_socket.send(error_message.encode())
                print(f"File {file_name} not found!")
                    



    def periodic_CheckIn(self):
      # periodically notifies the tracker of the seeder's availability
      with socket.socket(socket.AF_INET,socket.SOCK_DGRAM) as UDP_sock:
            while True:
                  message = f"ALIVE {self.file_name} {self.seeder_port}"
                  UDP_sock.sendto(message.encode(),(self.tracker_IP, self.tracker_port))
                  print(f"CheckIn sent!")
                  time.sleep(self.Checkin_Interval)# wait before sending notification again


    def run(self):
          
          #Step 1: Register seeder to tracker
          self.inform_Tracker()
          #Step 2: start periodic checkin in a different thread
          checkin_thread = threading.Thread(target= self.periodic_CheckIn,daemon = True)
          checkin_thread.start()

          #Step 3: Start TCP server to start file requests
          self.start_Server()

if __name__ == "__main__":
           seeder = Seeder(
                  tracker_IP="127.0.0.1",
                  tracker_port=1111,
                  seeder_IP="128.0.0.1",
                  seeder_port=7000,
                  Checkin_Interval=30
           )

           seeder.run()

       

          
          

         

                


          
          
          
                
          
            