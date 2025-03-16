import socket
import threading
import time
import os

# Corrected variable assignments
tracker_IP = "127.0.0.1"
tracker_port = 1111
seeder_IP = "127.0.0.1"
seeder_port = 7002
Checkin_Interval = 30
seeder_portUDP = 7003


class Seeder:
    def __init__(self, file_name: str, tracker_IP: str, tracker_port: int, 
                 seeder_IP: str, seeder_port: int, Checkin_Interval: int, seeder_portUDP: int):
        self.file_name = file_name
        self.chunks = {}
        self.tracker_IP = tracker_IP
        self.tracker_port = tracker_port
        self.seeder_IP = seeder_IP
        self.seeder_port = seeder_port
        self.Checkin_Interval = Checkin_Interval
        self.seeder_portUDP = seeder_portUDP


    def inform_Tracker(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as UDP_sock:  # Create a UDP socket
            UDP_sock.bind(("127.0.0.1", self.seeder_port))
            message = f"REGISTER {self.file_name} {self.seeder_IP} {self.seeder_portUDP}"
            UDP_sock.sendto(message.encode(), (self.tracker_IP, self.tracker_port))  # Send to tracker
            print(f"Registered with the tracker for the file: {self.file_name}")

    def start_Server(self):
        try:
            TCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            TCP.bind(("127.0.0.1", self.seeder_port))
            TCP.listen()
            print(f"Listening for connections on port {self.seeder_port}...")

            while True:
                client_socket, client_address = TCP.accept()  # Accept leecher connection
                print(f"Leecher {client_address} connected.")
                
                # Start a new thread to handle the client
                Client_thread = threading.Thread(target=self.Attend_clients, args=(client_socket, client_address))
                Client_thread.start()

        except Exception as e:
            print(f"Error: {e}")
        finally:
            TCP.close()

    def Attend_clients(self, client_socket, client_address):
        try:
            while True:
                request = client_socket.recv(1024).decode("utf-8")
                if not request or request.lower() == "close":
                    client_socket.send("closed".encode("utf-8"))
                    break

                print(f"Received request: {request}")
                client_socket.send("Accepted".encode("utf-8"))

                # Check if the request is for a file
                if request:
                    self.Send_files(request, client_socket)
                    
        except Exception as e:
            print(f"Error occurred while attending to client: {e}") 
        finally:
            client_socket.close()
            print(f"Connection to client {client_address} closed!")

    def Send_files(self, file_name, client_socket):
        client_socket.setblocking(False)
        try:
            with open(file_name, "rb") as file:
                while True:
                    chunk = file.read(1024)  # Read 1024 bytes at a time
                    if not chunk:
                        break  # Stop sending when the file is fully transferred
                    client_socket.sendall(chunk)  # Send chunk to client
                    print(f"Sent {len(chunk)} bytes to leecher.")
            print("File transfer complete!")
        except FileNotFoundError:
            error_message = "Error: File not found!"
            client_socket.send(error_message.encode())
            print(f"File {file_name} not found!")
        except Exception as e:
            error_message = f"Error: {str(e)}"
            client_socket.send(error_message.encode())
            print(f"Error during transfer: {e}")

   # def periodic_CheckIn(self):
    #    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as UDP_sock:
     #       while True:
      #          message = f"ALIVE {self.file_name} {self.seeder_port}"
       #         UDP_sock.sendto(message.encode(), (self.tracker_IP, self.tracker_port))
        #        print(f"Check-in sent!")
         #       time.sleep(self.Checkin_Interval)
    def trackerCheckIn(self):
        """Listen for 'Hello' messages from the tracker and respond with 'ALIVE'."""
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as UDP_sock:
            UDP_sock.bind((self.seeder_IP, self.seeder_portUDP))
            print(f"Listening for tracker messages on {self.seeder_IP}:{self.seeder_portUDP}...")
            while True:
                try:
                    message, address = UDP_sock.recvfrom(1024)
                    if message.decode() == "Hello":
                        print(f"Received 'Hello' from tracker at {address}")
                        UDP_sock.sendto(b"ALIVE", address)
                        print(f"Sent 'ALIVE' to tracker at {address}")
                except Exception as e:
                    print(f"Error in listen_for_tracker: {e}")

    def run(self):
        self.inform_Tracker()
        
        checkin_thread = threading.Thread(target=self.trackerCheckIn, daemon=True)
        checkin_thread.start()

        self.start_Server()

if __name__ == "__main__":
    # Correct instantiation with required parameters
    seeder = Seeder(
        file_name="example.txt",
        tracker_IP=tracker_IP,
        tracker_port=tracker_port,
        seeder_IP=seeder_IP,
        seeder_port=seeder_port,
        Checkin_Interval=Checkin_Interval,
        seeder_portUDP=seeder_portUDP

    )
    
    seeder.run()