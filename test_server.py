# This is a test file used to simulate a server for testing UDP
# sockets sending and receiving information.

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
	
	# Checks to make sure the data received is an integer
	try:
		int(data)
	except:
		print("ERROR: Data received is not an integer!")
		continue
	
	# Store data as an integer
	i_data = int(data)
		
	# Use the other socket to send the previous data + 1
	broadcast.send(str(i_data + 1).encode("utf-8"))
	
	if i_data == 100:
		break

# Close sockets
broadcast.close()
receive.close()
