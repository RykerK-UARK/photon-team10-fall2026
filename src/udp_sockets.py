import socket
import ipaddress

class UDPSocketPair:
    def __init__(self, network_address: str  = "127.0.0.1", broadcast_port: str = 7500, receive_port: str = 7501) -> None:
        # Attributes
        self.network_address = network_address
        self.broadcast_port = broadcast_port
        self.receive_port = receive_port
        self.buffer = None
        
        # Broadcast Socket Setup
        self.broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        
        # Receiving Socket Setup
        self.receive_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.receive_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # SO_REUSEADDR must be set before bind to take effect
        self.receive_socket.bind(("0.0.0.0", self.receive_port))
        self.receive_socket.setblocking(False)

    def get_network_address(self) -> str:
        return self.network_address
        
    def set_network_address(self, new_address: str) -> bool:
        try:
            ipaddress.ip_address(new_address)
        except ValueError:
            return False
        self.network_address = new_address
        return True

    def broadcast(self, data: str) -> None:
        try:
            self.broadcast_socket.sendto(str(data).encode("utf-8"), (self.network_address, self.broadcast_port))
        except ConnectionRefusedError:
            return
            
    def _receive(self) -> str:
        try:
            data, _ = self.receive_socket.recvfrom(1024)
        except BlockingIOError:
            return None  # Nothing = waiting
        
        try:
            return data.decode("utf-8").rstrip("\x00")
        except UnicodeDecodeError:
            return None
        
    def read_buffer(self) -> str:
        buffer_data = self.buffer
        self.buffer = None
        return buffer_data
        
    def peek_buffer(self) -> str:
        return self.buffer
        
    def update(self) -> None:
        data = self._receive()
        if data is None:
            return
        self.buffer = data

    def close(self) -> None:
        self.broadcast_socket.close()
        self.receive_socket.close()

