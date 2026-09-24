# This is the main file that will facilitate the entire software.

# Library imports
import socket
import ipaddress

### Socket Section Start ###

# Network Address
network_address = "127.0.0.1"

# Setup broadcast socket
broadcast = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
broadcast.connect((network_address, 7500))
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

#--------------------------
# Helper Functions
#--------------------------

# Broadcasts integer out on port 7500
def broadcast_code(code):
  broadcast.send(str(code).encode("utf-8"))

# Changes the target receiver (Verifies for valid address)
def set_network_address(new_address):
    global network_address
    try:
        ipaddress.ip_address(new_address) # Confirms valid IPadress
    except ValueError:
        return False
    network_address = new_address
    broadcast.connect((network_address, 7500))
    return True

# Confirms reception of broadcasted codes. Returns (shooter_id, hit_id) or Nothing
def poll_receive():
    try:
        data, _ = receive.recvfrom(1024)
    except BlockingIOError:
        return None # Nothing = waiting
    try:
        shooter, hit = data.decode("utf-8").split(":")
        return int(shooter), int(hit)
    except ValueError:
        return None # Bad packet received

# # Helper Functions Testing
# import time # Purely for testing purposes

# # Testing broadcast_code
# listener = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# listener.bind(("127.0.0.1", 7500))
# listener.settimeout(1)
# broadcast_code(1234)
# data, _ = listener.recvfrom(1024)
# print(data)
# listener.close()

# # Testing set_network_address
# print(set_network_address("127.0.0.1")) # Should print True
# print(set_network_address("hello")) # Should print False
# print(set_network_address("999.1.1.1")) # Should print False

# # Testing poll_receive
# sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# sender.sendto(b"43:53", ("127.0.0.1", 7501))
# time.sleep(0.1)
# print(poll_receive()) # Should return (43, 53)
# print(poll_receive()) # Should return None

# sender.sendto(b"hello", ("127.0.0.1", 7501))
# time.sleep(0.1)
# print(poll_receive()) # Should Return None
# sender.close()

# Close sockets
broadcast.close()
receive.close()

### Socket Section End ###
