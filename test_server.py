# This is a test file used to simulate a server for testing UDP
# sockets sending and receiving information.

# CURRENTLY, this test server just accepts  
# packets and prints them to the screen

# Library imports
import socket

# Setup broadcast socket
broadcast = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
broadcast.connect(("127.0.0.1", 7501))	
broadcast.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1) 

# Setup receiving socket
receive = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
receive.bind(("0.0.0.0", 7500)) # Should listen to UDP packets from any address at port 7501
receive.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

while True:
    # Get data in bytes
    b_data, address = receive.recvfrom(1024)
	
    # Convert data received to string
    data = str(b_data, "utf-8")
	
    # Print out the data to show it was recevied
    print(data)

# Close sockets
broadcast.close()
receive.close()
