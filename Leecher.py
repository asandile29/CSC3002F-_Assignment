#Asanda Ntuli
# 3 March 2025
# CSC3002F Assigment Networks

#importing all the needed imports

import socket
import os

#The tracker Details
tracker_ip = "127.0.0.1"
tracker_port_number = 12345

#The leecher Details.
Leecher_IP = "127.0.0.1"
Leecher_Port_Number = 1112

#The dirrectory to store my files
File_Downloads_Folder = "File_Downloads"

#Dirrectory to save all the list of the Seeders we find in the file
Seeder_List = {}

#telling the oparating System to create a dirrectory in my computer
os.makedirs(File_Downloads_Folder,exist_ok=True)

#Method to get the list of all the seeders with the name of the file.
def Request_Seeder_List(file_name):
 #Connecting to the tracker with UDP
 Tracker_Socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
 print(f"Connecting to Tracker with Port Number: {tracker_port_number} and a IP Address: {tracker_ip} ")

 #Sending the message to the Tracker.
 Tracker_Socket.sendto(f"Reguest {file_name}".encode(),(tracker_ip,tracker_port_number))
 Response,_= Tracker_Socket.recvfrom(1024)
 print("Fatching the responce....")

 if Response.decode()== "":
   print(f"No Seeders Found With File: {file_name}")
   return None
 else:
    Seeder_List= Response.decode().split(',')
    return Seeder_List
 


#The main if main menthod
if __name__ == "__main__":
    File_name = input("Please Enter The File You Want To Download:\n")
    Request_Seeder_List(File_name)
 