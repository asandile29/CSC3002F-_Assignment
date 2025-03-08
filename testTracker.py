import socket  # For networking (UDP communication)
import threading  # To handle multiple clients simultaneously

# Tracker configuration
TRACKER_IP = "localhost"  # Listen on all available network interfaces
TRACKER_PORT = 12000  # Port for UDP communication

# Dictionary to store file availability
# Format: {"file_name": ["seeder1_ip:seeder1_port", "seeder2_ip:seeder2_port"]}
file_registry = {'example_file.txt':["0.0.0.0:5000"] }

#Method to add the seeder list


def handle_client(data, client_address, udp_socket):
    """
    Handles incoming requests from leechers or seeders.

    - If the request is from a **leecher**, it returns a list of seeders for the requested file.
    - If the request is from a **seeder**, it registers the file availability in `file_registry`.
    """
    message = data.decode().strip()  # Decode incoming message

    # If the message starts with "REQUEST", it's from a leecher requesting seeders
    if message.startswith("REQUEST"):
        _, file_name = message.split(" ", 1)  # Extract the requested file name

        if file_name in file_registry:
            # Send the list of available seeders to the leecher
            seeder_list = ",".join(file_registry[file_name])  # Convert list to comma-separated string
            udp_socket.sendto(seeder_list.encode(), client_address)  # Send data back to leecher
            print(f"Sent seeders {seeder_list} for file '{file_name}' to {client_address}")
        else:
            # No seeders available for the requested file
            udp_socket.sendto(b"", client_address)  # Send an empty response
            print(f"No seeders available for '{file_name}' requested by {client_address}")

    # If the message starts with "REGISTER", it's from a seeder sharing a file
    elif message.startswith("REGISTER"):
        _, file_name, seeder_ip, seeder_port = message.split(" ")  # Extract file name & seeder details
        seeder_info = f"{seeder_ip}:{seeder_port}"  # Format seeder info as "IP:PORT"

        # Add the seeder to the registry for this file
        if file_name in file_registry:
            if seeder_info not in file_registry[file_name]:
                file_registry[file_name].append(seeder_info)
        else:
            file_registry[file_name] = [seeder_info]

        print(f"Registered seeder {seeder_info} for file '{file_name}'")

def start_tracker():
    """
    Starts the UDP tracker server to listen for connections from leechers and seeders.
    """
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Create a UDP socket
    udp_socket.bind((TRACKER_IP, TRACKER_PORT))  # Bind socket to tracker IP & port

    print(f"Tracker is running on {TRACKER_IP}:{TRACKER_PORT}")

    while True:
        data, client_address = udp_socket.recvfrom(2048)  # Receive data from any client

        # Create a new thread to handle each request
        client_thread = threading.Thread(target=handle_client, args=(data, client_address, udp_socket))
        client_thread.start()

# Run the tracker
if __name__ == "__main__":
    start_tracker()
