import socket
import os

# Trackers' address (Assuming it runs locally)
TRACKER_HOST = "127.0.0.1"
TRACKER_UDP_PORT = 1111  # The tracker listens for peer discovery on this port

# The directory where downloaded chunks are stored
DOWNLOADS_DIR = "downloads"

# Function to request available seeders from the tracker
def request_seeders():
    """
    Contacts the tracker to get a list of seeders.
    Returns a list of seeder addresses or None if no seeders are found.
    """
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Create a UDP socket
    udp_socket.sendto(b"REQUEST_PEERS", (TRACKER_HOST, TRACKER_UDP_PORT))  # Send request
    
    # Receive response from the tracker
    response, _ = udp_socket.recvfrom(2048)  
    seeders = response.decode().split(", ")  # Convert response to a list
    
    udp_socket.close()
    
    if seeders:
        print(f"Available seeders: {seeders}")
        return seeders
    else:
        print("No seeders found.")
        return None

# Function to download file chunks from a seeder
def download_from_seeder(seeder_ip, seeder_port, filename):
    """
    Connects to a seeder and downloads the file in chunks.
    Saves chunks to the downloads directory.
    """
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create a TCP socket
    
    try:
        print(f"Connecting to seeder at {seeder_ip}:{seeder_port}...")
        tcp_socket.connect((seeder_ip, seeder_port))  # Connect to seeder
        
        tcp_socket.send(filename.encode())  # Request file from seeder

        os.makedirs(DOWNLOADS_DIR, exist_ok=True)  # Ensure download directory exists

        chunk_index = 0
        while True:
            chunk_data = tcp_socket.recv(2048)  # Receive a chunk
            
            if not chunk_data:  # If no more data, break loop
                break

            chunk_path = os.path.join(DOWNLOADS_DIR, f"{filename}.chunk{chunk_index}")
            with open(chunk_path, "wb") as chunk_file:
                chunk_file.write(chunk_data)  # Save chunk to file
                
            print(f"Downloaded chunk {chunk_index}")
            chunk_index += 1

        print("Download completed. Merging chunks...")

    except Exception as e:
        print(f"Error while downloading: {e}")
    finally:
        tcp_socket.close()  # Close connection

# Function to merge file chunks into a single file
def merge_chunks(filename):
    """
    Merges all the downloaded chunks into the final file.
    """
    final_file_path = os.path.join(DOWNLOADS_DIR, filename)

    with open(final_file_path, "wb") as final_file:
        chunk_index = 0
        while True:
            chunk_path = os.path.join(DOWNLOADS_DIR, f"{filename}.chunk{chunk_index}")
            if not os.path.exists(chunk_path):
                break  # Stop if no more chunks
            
            with open(chunk_path, "rb") as chunk_file:
                final_file.write(chunk_file.read())  # Append chunk data to final file
            
            os.remove(chunk_path)  # Remove chunk after merging
            chunk_index += 1

    print(f"File {filename} reconstructed successfully!")

# Function to transform leecher into seeder
def become_seeder(filename):
    """
    After downloading a file, the leecher can act as a seeder.
    It opens a TCP socket to serve the file to other leechers.
    """
    SEEDER_PORT = 5000  # Port for seeding files
    seeder_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    seeder_socket.bind(("0.0.0.0", SEEDER_PORT))  # Bind to all interfaces
    seeder_socket.listen(5)

    print(f"Now seeding '{filename}' on port {SEEDER_PORT}...")

    while True:
        client_socket, client_address = seeder_socket.accept()
        print(f"Serving file to {client_address}")

        with open(os.path.join(DOWNLOADS_DIR, filename), "rb") as file:
            while chunk := file.read(2048):  # Read and send file in chunks
                client_socket.send(chunk)

        client_socket.close()

# Main execution
if __name__ == "__main__":
    
    filename = input('Please enter the file name you want to download:')  # The file we want to download

    seeders = request_seeders()  # Get list of available seeders

    if seeders:
        seeder_ip = seeders[0].split(":")[0]  # Extract seeder IP from tracker response
        seeder_port = 5000  # Assuming all seeders use port 5000

        download_from_seeder(seeder_ip, seeder_port, filename)  # Download the file
        merge_chunks(filename)  # Reconstruct the file
        become_seeder(filename)  # Start seeding the file for others
