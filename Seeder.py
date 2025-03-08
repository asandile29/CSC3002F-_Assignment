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
               self.split_file()

       
    def split_file(self, file_name, chunk_size = 512 *1024):
            chunks = {}
            with open(file_name, "rb") as file:
                chunk_id = 0
                while chunk := file.read(chunk_size):  # Read in chunks
                    self.chunks[chunk_id] = chunk
                    chunk_id += 1
            return chunks  # Returns a dictionary {chunk_id: chunk_data}
    

    
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

                  TCP.bind((self.seeder_IP, self.seeder_port))
                  #listen for incoming connections
                  TCP.listen()
                  print(f"Listening to connections from port:{self.seeder_port}...")

                  #we want to keep listening for connections
                  while True:
                        client_sock, client_address = TCP.accept()#accept leecher connection
                        print(f"Leecher {client_address} connected.")
                        #start new thread to handle the client
                        thread = threading.Thread(target= self.Attend_clients(), args = (client_sock,client_address))
                        thread.start()

          except Exception as e:
                print(f"Error: {e}")
              
          finally:
                TCP.close() 

    def Attend_clients(self, client_socket, client_address) :
          try:
                while True:
                      #receive and print client messages
                      request = client_socket.recv(1024).decode("utf-8")
                      if not request or request.lower == "close":
                            client_socket.send("closed".encode("utf-8"))
                            break
                      print(f"Received: {request}")
                      # send response to client
                      client_socket.send("Accepted".encode("utf-8"))
                      try:
                            chunk_id = int(request) # assume request is a chunk id
                            self.Send_files(client_socket,chunk_id)
                      except ValueError:
                            client_socket.send("Invalid request".encode("utf-8"))
                            
          except Exception as e:
                print(f"Error when handling client: {e}") 
          finally:
                client_socket.close()
                print(f"Connection to client ({client_address[0]:{client_address[1]}}) closed!") 


    def Send_files(self, client_socket, file_name, chunk_id):
          #sending the file chunks to the leecher
          try:
                if chunk_id in self.chunks:
                       client_socket.send(self.chunks[chunk_id])
                       print(f"Sent chunk: {chunk_id} to Leecher")
                else:
                      client_socket.send(b"Invalid chunk!")
                         
          except Exception as e:
            print(f"Error in sending chunk: {e}")



    def periodic_CheckIn(self):
      # periodically notifies the tracker of the seeder's availability
      with socket.socket(socket.AF_INET,socket.SOCK_DGRAM) as UDP_sock:
            while True:
                  message = f"ALIVE {self.file_name} {self.seeder_port}"
                  UDP_sock.sendto(message.encode(),(self.tracker_IP, self.tracker_port))
                  print(f"Heartbeat sent!")
                  time.sleep(self.Checkin_Interval)# wait before sending notification again


    def run(self):
          #Step 1: split file has already been done in __init__
          #Step 2: Register seeder to tracker
          self.inform_Tracker()
          #start periodic checkin in a different thread
          checkin_thread = threading.Thread(target= periodic_CheckIn,daemon = True)
          checkin_thread.start()

          #Step 3: Start TCP server to start file requests
          self.start_Server()

    if __name__ == "__main__":
           seeder = Seeder(
                  tracker_IP="127.0.0.1",
                  tracker_port=6000,
                  seeder_IP="127.0.0.1",
                  seeder_port=7000,
                  Checkin_Interval=30
           )

           seeder.run()

       

          
          

         

                


          
          
          
                
          
            