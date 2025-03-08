import socket  # For networking (TCP/UDP connections)
import hashlib  # For verifying file integrity using SHA-256
import os  # For handling file storage
import threading  # To download chunks in parallel

# Tracker details (assumed to be running on this IP and port)
TRACKER_IP = "localhost"  # IP address of the tracker
TRACKER_PORT = 1200  # UDP port for tracker communication

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
        response, _ = udp_socket.recvfrom(1024)  # Expect a short response
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


def verify_file_integrity(file_name, expected_hash):
    """
    Verifies the integrity of the downloaded file by computing its SHA-256 hash.
    
    Steps:
    1. Reads the entire downloaded file.
    2. Computes its SHA-256 hash.
    3. Compares the computed hash with the expected hash.
    """
    file_path = os.path.join(DOWNLOAD_FOLDER, file_name)
    sha256 = hashlib.sha256()

    with open(file_path, "rb") as f:
        while chunk := f.read(4096):  # Read file in 4 KB chunks
            sha256.update(chunk)  # Update hash with file content

    computed_hash = sha256.hexdigest()  # Get final hash value
    return computed_hash == expected_hash  # Return True if hash matches


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

    # Step 2: Download chunks from multiple seeders (parallel downloads)
    threads = []
    for i in range(total_chunks):
        seeder_info = seeder_list[i % len(seeder_list)].split(":")  # Round-robin seeder selection
        seeder_ip, seeder_port = seeder_info[0], seeder_info[1]

        # Create a thread to download a chunk from a specific seeder
        thread = threading.Thread(target=download_chunk, args=(seeder_ip, seeder_port, file_name, i))
        threads.append(thread)
        thread.start()

    # Wait for all chunks to be downloaded before proceeding
    for thread in threads:
        thread.join()

    # Step 3: Merge chunks into a single file
    merge_chunks(file_name, total_chunks)

    # Step 4: Verify file integrity (optional)
    expected_hash = "expected_sha256_hash_here"  # Replace with actual hash from the tracker
    if verify_file_integrity(file_name, expected_hash):
        print("File integrity verified. Download successful!")
    else:
        print("File integrity check failed. The file may be corrupted.")


# Example usage
if __name__ == "__main__":
    file_to_download = "example_file.txt"  # Name of the file to download
    total_file_chunks = 4  # Assume file is split into 4 chunks
    leecher_main(file_to_download, total_file_chunks)
