"""UDP socket helpers for the Photon laser-tag system."""
import socket
import ipaddress

BROADCAST_PORT = 7500
RECEIVE_PORT = 7501

network_address = "127.0.0.1"

# Broadcast socket
broadcast = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
broadcast.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

# Receiving socket (SO_REUSEADDR must be set before bind to take effect)
receive = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
receive.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
receive.bind(("0.0.0.0", RECEIVE_PORT))
receive.setblocking(False)

def get_network_address() -> str:
    return network_address


def set_network_address(new_address: str) -> bool:
    global network_address
    try:
        ipaddress.ip_address(new_address)
    except ValueError:
        return False
    network_address = new_address
    return True


def broadcast_code(code) -> None:
    try:
        broadcast.sendto(str(code).encode("utf-8"), (network_address, BROADCAST_PORT))
    except ConnectionRefusedError:
        return


def poll_receive():
    try:
        data, _ = receive.recvfrom(1024)
    except BlockingIOError:
        return None  # Nothing = waiting
    try:
        shooter, hit = data.decode("utf-8").split(":")
        return int(shooter), int(hit)
    except ValueError:
        return None  # Bad packet


def close_sockets() -> None:
    broadcast.close()
    receive.close()
