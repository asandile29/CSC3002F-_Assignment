import socket
import threading
import time
import os

# Port and IP assignments
tracker_ip = '127.0.0.1'  # Tracker's IP
tracker_port = 1111       # Tracker's port
leacher_portUDP = 2777    # Leecher's UDP port
seeder_portUDP = 2778     # Seeder's UDP port
leacher_port = 7373       # Leecher's TCP port
seeder_port = 7374        # Seeder's TCP port
leacher_IP = '127.0.0.1'  # Leecher's IP
seeder_ip = '127.0.0.1'   # Seeder's IP

def request_seeder_list(file_name):
    """Request seeders from the tracker."""
    leecher_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #leecher_socket.bind(("127.0.0.1", leacher_portUDP))

    # Send request to tracker
    request_msg = f"Request {file_name}"
    leecher_socket.sendto(request_msg.encode(), (tracker_ip, tracker_port))

    # Receive seeder list
    seeder_data, _ = leecher_socket.recvfrom(1024)
    seeder_list = seeder_data.decode()

    leecher_socket.close()
    
    return seeder_list.split(",") if seeder_list else []

def download_file(seeder_ip, seeder_port, file_name):
    """Download a file from a seeder via TCP."""
    try:
        seeder_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        seeder_socket.connect((seeder_ip, int(seeder_port)))

        # Request file from the seeder
        seeder_socket.sendall(file_name.encode())

        # Receive the file data
        with open(f"{file_name}1", "wb") as file:
            while True:
                data = seeder_socket.recv(1024)
                if not data:
                    break  # Connection closed by seeder
                file.write(data)
                file.flush()
                break
        print(f"File '{file_name}' downloaded successfully! Saved as {file_name}1")
    except Exception as e:
        print(f"Failed to download from {seeder_ip}:{seeder_port} - {e}")
    finally:
        seeder_socket.close()

class Seeder:
    def __init__(self, file_name: str, tracker_ip: str, tracker_port: int, 
                 seeder_IP: str, seeder_port: int, Checkin_Interval: int, seeder_portUDP: int, fname: str):
        self.file_name = file_name
        self.tracker_ip = tracker_ip
        self.tracker_port = tracker_port
        self.seeder_IP = seeder_IP
        self.seeder_port = seeder_port
        self.Checkin_Interval = Checkin_Interval
        self.seeder_portUDP = seeder_portUDP
        self.fname = fname

    def inform_Tracker(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as UDP_sock:
            UDP_sock.bind(("127.0.0.1", 0))
            self.seeder_IP,self.seeder_port=  UDP_sock.getsockname()
            message = f"REGISTER {self.file_name} {self.seeder_IP} {self.seeder_portUDP}"
            UDP_sock.sendto(message.encode(), (self.tracker_ip, self.tracker_port))
            print(f"Registered with the tracker for the file: {self.file_name}")

    def start_Server(self):
        try:
            TCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            TCP.bind(("127.0.0.1", 0))
            self.seeder_IP,self.seeder_port=  TCP.getsockname()
            TCP.listen()
            print(f"Listening for connections on port {self.seeder_port}...")

            while True:
                client_socket, client_address = TCP.accept()
                print(f"Leecher {client_address} connected.")
                threading.Thread(target=self.Attend_clients, args=(client_socket, client_address, self.fname)).start()
        except Exception as e:
            print(f"Error: {e}")
        finally:
            TCP.close()

    def Attend_clients(self, client_socket, client_address, fname):
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
        try:
            with open(file_name, "rb") as file:
                while True:
                    chunk = file.read(1024)
                    if not chunk:
                        break
                    client_socket.sendall(chunk)
            print("File transfer complete!")
        except FileNotFoundError:
            error_message = "Error: File not found!"
            client_socket.send(error_message.encode())
            print(f"File {file_name} not found!")
        except Exception as e:
            error_message = f"Error: {str(e)}"
            client_socket.send(error_message.encode())
            print(f"Error during transfer: {e}")

    def trackerCheckIn(self):
        """Listen for 'Hello' messages from the tracker and respond with 'ALIVE'."""
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as UDP_sock:
            UDP_sock.bind((self.seeder_IP, 0))
            ip, port = UDP_sock.getsockname()
            print(f"Listening for tracker messages on {ip}:{port}...")
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
    file_name = input("Enter the file you want to download: ").strip()
    
    seeders = request_seeder_list(file_name)
    
    if not seeders:
        print(f"No seeders available for '{file_name}'.")
    else:
        print(f"Available seeders: {seeders}")
        seeder_ip, seeder_port = seeders[0].split(":")  # Pick the first seeder
        print(f"Downloading from {seeder_ip}:{seeder_port}...")
        download_file(seeder_ip, seeder_port, file_name)

    seeder = Seeder(
        file_name=file_name,
        tracker_ip=tracker_ip,
        tracker_port=tracker_port,
        seeder_IP=seeder_ip,
        seeder_port=seeder_port,
        Checkin_Interval=30,
        seeder_portUDP=seeder_portUDP,
        fname=f"{file_name}1"
    )
        
    seeder.run()