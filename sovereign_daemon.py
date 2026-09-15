import socket
import os
import torch
import pickle
import struct
import threading
import concurrent.futures
from sovereign_runtime import SovereignRuntimeEngine

SOCKET_PATH = "/tmp/sovereign_runtime.sock"
engine_lock = threading.Lock()

def handle_client(conn, engine):
    try:
        raw_len = conn.recv(4)
        if not raw_len or len(raw_len) < 4:
            return
        length = struct.unpack("!I", raw_len)[0]
        data = conn.recv(length)
        payload_packet = pickle.loads(data)
        
        x_coord = payload_packet.get("x", 12345678)
        y_coord = payload_packet.get("y", 87654321)
        text = payload_packet.get("text", "PI.DEV:DEFAULT_CYCLE")
        
        # Synchronize access to MPS device execution across concurrent threads
        with engine_lock:
            result = engine.execute_sovereign_cycle(x_coord, y_coord, text)
        
        response = pickle.dumps(result)
        conn.sendall(struct.pack("!I", len(response)) + response)
    except Exception as e:
        print(f"[error] {e}")
        try:
            err_response = pickle.dumps({"error": str(e)})
            conn.sendall(struct.pack("!I", len(err_response)) + err_response)
        except:
            pass
    finally:
        conn.close()

def run_sovereign_daemon():
    if os.path.exists(SOCKET_PATH):
        os.unlink(SOCKET_PATH)
        
    engine = SovereignRuntimeEngine()
    
    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server.bind(SOCKET_PATH)
    server.listen(128)
    print(f"[ok] Sovereign RAM Daemon active with thread-safe MPS lock on {SOCKET_PATH}")
    
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=16)
    
    try:
        while True:
            conn, _ = server.accept()
            executor.submit(handle_client, conn, engine)
    finally:
        server.close()
        if os.path.exists(SOCKET_PATH):
            os.unlink(SOCKET_PATH)

if __name__ == "__main__":
    run_sovereign_daemon()
