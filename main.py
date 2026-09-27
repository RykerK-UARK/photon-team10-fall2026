"""Main entry point for the Photon laser-tag application."""
# Library imports
import socket
import ipaddress
from player_database import playerDatabase
from player_entry import run_player_entry

# Create a database connection for the application
database = playerDatabase()

def main() -> None:
    # Sprint 2 UI entry point.
    # Database/UDP integration can be passed to run_player_entry as a callback.
    run_player_entry(add_player, set_network_address)
    
    # TEST: Print all players in the database and then clear the database
    database.print_all_players()
    database.clear_players()
    
    # TEST: Print current Network Address
    print(network_address)
    
    shutdown()

### Socket Section Start ###

# Network Address
network_address = "127.0.0.1"
BROADCAST_PORT = 7500

# Setup broadcast socket
broadcast = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
broadcast.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1) # Allow broadcasting

# Setup receiving socket
receive = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
receive.bind(("0.0.0.0", 7501))
receive.setblocking(False)
receive.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Allow quick restart

#--------------------------
# Helper Socket Functions
#--------------------------

# Broadcasts integer out on port 7500
def broadcast_code(code):
    try:
        broadcast.sendto(str(code).encode("utf-8"), (network_address, BROADCAST_PORT))
    # Could not connect to server (probably not set up)
    except ConnectionRefusedError:
        return

# Add a player to PostgreSQL, then announces the equipment ID to the UDP server
def add_player(player): # player_id, codename, equipment_id
    # Do not try database operations if connection failed at startup.
    if database.conn is None or database.cursor is None:
        print("PostgreSQL is unavailable.")
        return False

	# Get values from the player object
    player_id = database.get_new_player_id(player.team)
    equipment_id = player.equipment_id
    codename = player.codename

    if not database.add_player(player_id, codename):
        return False

    broadcast_code(equipment_id)
    return True

# Changes the target receiver (Verifies for valid address)
def set_network_address(new_address) -> bool:
    global network_address
    try:
        ipaddress.ip_address(new_address) # Confirms valid IPadress
    except ValueError:
        return False
    network_address = new_address
    
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

## Collect two players for the sprint 2 database entry test
#def add_two_players():
#    # Stop if PostgreSQL could not be reached.
#    if database.conn is None or database.cursor is None:
#        print("Start PostgreSQL or correct the database host.")
#        return
#
#    for i in range(2):
#        while True:
#            try:
#                player_id = int(input(f"Enter player {i+1} ID: "))
#                codename = input(f"Enter player {i+1} codename: ").strip()
#                equipment_id = int(input(f"Enter player {i+1} equipment ID: "))
#
#                if not codename:
#                    print("Codename cannot be empty.")
#                    continue
#
#                if add_player(player_id, codename, equipment_id):
#                    print(f"Player {player_id} added.")
#                    break
#
#                print(f"Player ID {player_id} already exists. Try again.")
#            except ValueError:
#                print("Player ID and equipment ID must be integers. Try again.")


# Close sockets
def shutdown():
    database.disconnect()
    broadcast.close()
    receive.close()

### Socket Section End ###

# Run Main
if __name__ == "__main__":
    main()
