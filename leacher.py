import socket  # For networking (TCP/UDP connections)
import hashlib  # For verifying file integrity using SHA-256
import os  # For handling file storage
import threading  # To download chunks in parallel

# Tracker details (assumed to be running on this IP and port)
TRACKER_IP = "localhost"  # IP address of the tracker
TRACKER_PORT = 12000  # UDP port for tracker communication

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
