import socket  # For networking (TCP communication)
import threading  # To handle multiple leechers
import os  # To check file existence

# Seeder Configuration
SEEDER_IP = "0.0.0.0"  # Listen on all network interfaces
SEEDER_PORT = 5000  # Port to serve files

# File to be shared (Ensure this file exists in the seeder’s directory)
FILE_NAME = "example_file.txt"

def handle_leecher(client_socket):
    """
    Handles file requests from leechers.
    Sends the requested file in chunks.
    """
    request = client_socket.recv(1024).decode().strip()  # Receive file request

    if request == FILE_NAME and os.path.exists(FILE_NAME):
        print(f"Leecher requested: {FILE_NAME}. Sending file...")

        with open(FILE_NAME, "rb") as file:
            while chunk := file.read(1024):  # Read and send file in 1024-byte chunks
                client_socket.send(chunk)
        
        print("File sent successfully!")
    else:
        print("File not found. Sending error message.")
        client_socket.send(b"ERROR: File not found.")  # Inform leecher of error

    client_socket.close()  # Close the connection

def start_seeder():
    """
    Starts the TCP server to handle file requests from leechers.
    """
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create a TCP socket
    server_socket.bind((SEEDER_IP, SEEDER_PORT))  # Bind to IP and Port
    server_socket.listen(5)  # Listen for incoming connections (max 5)

    print(f"Seeder is running on {SEEDER_IP}:{SEEDER_PORT}, sharing '{FILE_NAME}'")

    while True:
        client_socket, client_address = server_socket.accept()  # Accept leecher connection
        print(f"Connected to leecher: {client_address}")

        # Handle each leecher request in a new thread
        client_thread = threading.Thread(target=handle_leecher, args=(client_socket,))
        client_thread.start()

# Run the seeder
if __name__ == "__main__":
    start_seeder()
