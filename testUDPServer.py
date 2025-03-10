from socket import *
import json  # To serialize the list before sending

# Server Port number
serverPort = 12000

# Seeders List in the network system.
Seeder_list = ["Seeder1", "Seeder2", "Seeder3"]  # Example data

# Create a UDP server socket
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('', serverPort))

print("The server is ready to receive requests...")

while True:
    try:
        # Receive file request from client
        file_name, clientAddress = serverSocket.recvfrom(2048)
        file_name = file_name.decode()

        print(f"Received request for file: {file_name} from {clientAddress}")

        # Simulate loading
        for i in range(4):
            print(f"Loading{'.' * (i+1)}")

        # Convert the Seeder list to JSON and send it
        Seeder_list_bytes = json.dumps(Seeder_list).encode()
        serverSocket.sendto(Seeder_list_bytes, clientAddress)

        print(f"Seeder list sent to {clientAddress}")

    except KeyboardInterrupt:
        print("\nServer manually stopped.")
        break  # Exit the loop safely

# Close the server socket when exiting
serverSocket.close()
print("Server has been shut down.")

