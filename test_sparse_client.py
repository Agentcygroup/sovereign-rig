import socket
import struct
import pickle
import torch
import time

SOCKET_PATH = "/tmp/sparse_engine.sock"

def test_daemon():
    client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    client.connect(SOCKET_PATH)
    
    tensor = torch.randn(1, 64, 256)
    data = pickle.dumps(tensor)
    
    start = time.time()
    client.sendall(struct.pack("!I", len(data)) + data)
    
    raw_len = client.recv(4)
    length = struct.unpack("!I", raw_len)[0]
    response_data = client.recv(length)
    output_tensor = pickle.loads(response_data)
    elapsed = (time.time() - start) * 1000
    
    client.close()
    print(f"[ok] IPC round-trip complete in {elapsed:.2f} ms")
    print(f"[ok] Received output tensor shape: {output_tensor.shape}")

if __name__ == "__main__":
    test_daemon()
