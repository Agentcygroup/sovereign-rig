import socket
import os
import torch
import pickle
import struct
from sparse_engine import SparseLinearAttentionRouter

SOCKET_PATH = "/tmp/sparse_engine.sock"

def run_daemon():
    if os.path.exists(SOCKET_PATH):
        os.unlink(SOCKET_PATH)
        
    device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
    print(f"[ok] Loading Sparse Engine into RAM daemon on {device}...")
    engine = SparseLinearAttentionRouter().to(device)
    engine.eval()
    
    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server.bind(SOCKET_PATH)
    server.listen(1)
    print(f"[ok] Sparse RAM Daemon listening on {SOCKET_PATH}")
    
    try:
        while True:
            conn, _ = server.accept()
            try:
                raw_len = conn.recv(4)
                if not raw_len:
                    conn.close()
                    continue
                length = struct.unpack("!I", raw_len)[0]
                data = conn.recv(length)
                tensor_data = pickle.loads(data)
                
                with torch.no_grad():
                    input_tensor = tensor_data.to(device)
                    output_tensor = engine(input_tensor).cpu()
                    
                response = pickle.dumps(output_tensor)
                conn.sendall(struct.pack("!I", len(response)) + response)
            except Exception as e:
                print(f"[error] {e}")
            finally:
                conn.close()
    finally:
        server.close()
        if os.path.exists(SOCKET_PATH):
            os.unlink(SOCKET_PATH)

if __name__ == "__main__":
    run_daemon()
