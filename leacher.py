import socket

TRACKER_IP = '127.0.0.1'  # Trackers IP
TRACKER_PORT = 1111     # Same port as the tracker

def request_seeder_list(file_name):
    """Request seeders from the tracker."""
    leecher_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Send request to tracker
    request_msg = f"Request {file_name}"
    leecher_socket.sendto(request_msg.encode(), (TRACKER_IP, TRACKER_PORT))

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
        message, address = seeder_socket.recvfrom(1024)
        print(message.decode())

        with open(f"downloaded_{file_name}", "wb") as file:
            while True:
                data = seeder_socket.recv(1024)
                if not data:
                    print(f"No Data found in File: {file_name} ")
                    seeder_socket.close()
                    break

                file.write(data)

        print(f"File '{file_name}' downloaded successfully!")
        seeder_socket.close()
    
    except Exception as e:
        print(f"Failed to download from {seeder_ip}:{seeder_port} - {e}")

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
