import socket
import threading

# Dictionary to store registered seeders (Format: {file_name: [(ip, port), (ip, port), ...]})
peers = {}
peers_lock = threading.Lock()  # Prevent race conditions

# Tracker listens on this port for both seeders and leechers
tracker_port = 12345
tracker_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
tracker_socket.bind(('127.0.0.1', tracker_port))

print(f"Tracker running on port {tracker_port}...")

def handle_requests():
    """Handles both seeder registration and leecher requests."""
    while True:
        try:
            message, address = tracker_socket.recvfrom(1024)
            message = message.decode()
            print(f"Message from {address}: {message}")

            if message.startswith("Register"):
                # Seeder registers a file
                file_name = message.split(" ")[1]

                with peers_lock:
                    if file_name in peers:
                        if address not in peers[file_name]:
                            peers[file_name].append(address)
                    else:
                        peers[file_name] = [address]

                print(f"Seeder {address} registered for file '{file_name}'.")

            elif message.startswith("Request"):
                # Leecher requests a file
                file_name = message.split(" ")[1]

                with peers_lock:
                    if file_name in peers and peers[file_name]:
                        seeder_list = ",".join(f"{ip}:{port}" for ip, port in peers[file_name])
                        tracker_socket.sendto(seeder_list.encode(), address)
                        print(f"Sent seeders '{seeder_list}' to {address}.")
                    else:
                        tracker_socket.sendto(b"", address)
                        print(f"No seeders found for '{file_name}'.")

        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    try:
        threading.Thread(target=handle_requests, daemon=True).start()
        while True:
            pass  # Keep tracker running
    except KeyboardInterrupt:
        print("\nTracker shutting down...")
    finally:
        tracker_socket.close()
