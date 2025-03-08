import socket  # For networking (TCP/UDP connections)
import hashlib  # For verifying file integrity using SHA-256
import os  # For handling file storage
import threading  # To download chunks in parallel

# Tracker details (assumed to be running on this IP and port)
TRACKER_IP = "localhost"  # IP address of the tracker
TRACKER_PORT = 12000  # UDP port for tracker communication

Leecher_IP= "192.168.1.1"
Leecher_Port= 4000

# File chunk size (each chunk is 512 KB)
CHUNK_SIZE = 512 * 1024  # 512 KB

# Directory to store downloaded file chunks
DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)  # Create the folder if it doesn't exist


def request_seeder_list(file_name):
    """
    Contacts the tracker via UDP to get a list of seeders that have the requested file.
    
    Steps:
    1. Sends a request message to the tracker.
    2. Receives a list of seeders (IP:Port format).
    3. Returns the seeder list or an empty list if no response.
    """
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Create a UDP socket

    try:
        message = f"REQUEST {file_name}".encode()  # Format request message
        udp_socket.sendto(message, (TRACKER_IP, TRACKER_PORT))  # Send request to tracker

        # Set a timeout in case the tracker is unresponsive
        udp_socket.settimeout(5)

        # Receive response from tracker
        response, _ = udp_socket.recvfrom(2048)  # Expect a short response
        seeder_list = response.decode().split(",")  # Convert response to list
        
        return seeder_list if seeder_list[0] else []  # Return list of seeders (if available)

    except socket.timeout:
        print("Tracker did not respond in time.")
        return []  # No seeders available
    finally:
        udp_socket.close()  # Close the socket
def download_chunk(seeder_ip, seeder_port, file_name, chunk_index):
    """
    Connects to a seeder via TCP to request and download a specific chunk of the file.

    Steps:
    1. Creates a TCP connection to the seeder.
    2. Sends a request message for a specific chunk of the file.
    3. Receives the chunk and saves it to a file.
    4. Closes the connection.
    """
    try:
        tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create TCP socket
        tcp_socket.connect((seeder_ip, int(seeder_port)))  # Connect to seeder

        # Format request message: "GET file_name chunk_index"
        request_message = f"GET {file_name} {chunk_index}".encode()
        tcp_socket.sendall(request_message)  # Send request to seeder

        # Receive chunk data from seeder
        chunk_data = tcp_socket.recv(CHUNK_SIZE)  # Receive a full chunk (or less)

        # Save chunk to file
        chunk_path = os.path.join(DOWNLOAD_FOLDER, f"{file_name}.chunk{chunk_index}")
        with open(chunk_path, "wb") as chunk_file:
            chunk_file.write(chunk_data)

        print(f"Downloaded chunk {chunk_index} from {seeder_ip}:{seeder_port}")

        tcp_socket.close()  # Close connection after receiving the chunk

    except Exception as e:
        print(f"Error downloading chunk {chunk_index} from {seeder_ip}: {e}")


def merge_chunks(file_name, total_chunks):
    """
    Merges all downloaded chunks into a single file.

    Steps:
    1. Opens a new file for writing the complete data.
    2. Reads each chunk file and writes its contents into the complete file.
    3. Deletes chunk files after merging.
    """
    complete_file_path = os.path.join(DOWNLOAD_FOLDER, file_name)

    with open(complete_file_path, "wb") as complete_file:
        for i in range(total_chunks):
            chunk_path = os.path.join(DOWNLOAD_FOLDER, f"{file_name}.chunk{i}")
            
            with open(chunk_path, "rb") as chunk_file: 
                complete_file.write(chunk_file.read())  # Append chunk data to final file
            
            os.remove(chunk_path)  # Remove the chunk file after merging

    print(f"File {file_name} successfully assembled!")


#Converting to a Seeder after recienving he chunks of data.

def notify_tracker_of_seeding(tracker_ip, tracker_port, leecher_ip, leecher_port,file_name):
    """
    Notify the tracker that this leecher is now a seeder and is available to provide file chunks.
    """
    message = f"SEEDER {file_name} {leecher_ip}:{leecher_port}"
    tracker_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    tracker_socket.sendto(message.encode(), (tracker_ip, tracker_port))
    tracker_socket.close()

    print(f"Leecher {Leecher_IP} has be converted to a Seeder...")

def leecher_main(file_name, total_chunks):
    """
    Main function for the leecher:
    
    Steps:
    1. Requests a list of seeders from the tracker.
    2. Downloads chunks from multiple seeders in parallel.
    3. Merges the chunks into a complete file.
    4. (Optional) Verifies file integrity.
    """
    # Step 1: Request list of seeders from the tracker
    seeder_list = request_seeder_list(file_name)

    if not seeder_list:
        print("No seeders available for this file.")
        return

    print(f"Found seeders: {seeder_list}")

    notify_tracker_of_seeding(Leecher_IP, Leecher_Port, TRACKER_IP, TRACKER_PORT,file_name)


# Example usage
if __name__ == "__main__":
    file_to_download = "example_file.txt"  # Name of the file to download
    total_file_chunks = 4  # Assume file is split into 4 chunks
    leecher_main(file_to_download, total_file_chunks)
