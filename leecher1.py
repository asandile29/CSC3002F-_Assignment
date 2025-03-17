import socket
import os

# Tracker details
tracker_ip = "127.0.0.1"
tracker_port = 1111

# Leecher's download directory
DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)  # Create folder if it doesn't exist

def request_file(file_name):
    """Sends a request to the tracker for a specific file and retrieves the list of seeders."""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.sendto(f"Request {file_name}".encode(), (tracker_ip, tracker_port))
        response, _ = sock.recvfrom(1024)  # Receive the list of seeders

        if not response:
            print(f"No seeders found for '{file_name}'.")
            return None

        seeder_list = response.decode().split(",")  # Convert seeder list to usable format
        print(f"Available seeders for '{file_name}': {seeder_list}")
        return seeder_list

def download_from_seeder(seeder_ip, seeder_port, file_name):
    """Connects to a seeder and downloads the file in chunks."""
    seeder_address = (seeder_ip, int(seeder_port))
    
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.sendto(f"Download {file_name}".encode(), seeder_address)
        
        chunk_number = 0
        while True:
            chunk, _ = sock.recvfrom(4096)  # Receive file chunk
            
            if chunk == b"END":  
                print("Download complete!")
                break  # Stop when all chunks are received
            
            chunk_path = os.path.join(DOWNLOAD_FOLDER, f"{file_name}.chunk{chunk_number}")
            with open(chunk_path, "wb") as f:
                f.write(chunk)

            print(f"Received chunk {chunk_number}")
            chunk_number += 1
        
    merge_chunks(file_name)

def merge_chunks(file_name):
    """Reassembles the downloaded chunks into a complete file."""
    with open(os.path.join(DOWNLOAD_FOLDER, file_name), "wb") as final_file:
        chunk_number = 0
        while True:
            chunk_path = os.path.join(DOWNLOAD_FOLDER, f"{file_name}.chunk{chunk_number}")
            if not os.path.exists(chunk_path):
                break  # Stop when no more chunks are found

            with open(chunk_path, "rb") as chunk_file:
                final_file.write(chunk_file.read())

            os.remove(chunk_path)  # Cleanup chunk files
            chunk_number += 1

    print(f"File '{file_name}' successfully assembled!")

if __name__ == "__main__":
    file_name = input("Enter the file you want to download: ")
    seeders = request_file(file_name)

    if seeders:
        for seeder in seeders:
            ip, port = seeder.split(":")
            print(f"Attempting to download from {ip}:{port}...")
            download_from_seeder(ip, port, file_name)
            break  # Stop after first successful download
