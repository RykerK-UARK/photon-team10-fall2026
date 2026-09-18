# This is the main file that will facilitate the entire software.

# Library imports
import socket

### Socket Section Start ###

# Setup broadcast socket
broadcast = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
broadcast.connect(("127.0.0.1", 7500))
broadcast.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1) # Allow broadcasting

# Setup receiving socket
receive = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
receive.bind(("0.0.0.0", 7501))
receive.setblocking(False)
receive.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Allow quick restart

# Test code, designed to work with test_server.py 
#num = 0
#while True:
# 	# Send current number
#	broadcast.send(str(num).encode("utf-8"))
#	print(f"{num} sent")
#	
#	# Receive server response from other socket
#	data, address = receive.recvfrom(1024)
#	num = int(str(data, "utf-8"))
#	print(f"{num} received")
#	
#	# If the received number is greater than 5, end the process
#	if num > 5:
#		print("Process terminated")
#		break

# Close sockets
broadcast.close()
receive.close()

### Socket Section End ###
