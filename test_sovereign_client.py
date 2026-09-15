import socket
import pickle
import struct
import time

SOCKET_PATH = "/tmp/sovereign_runtime.sock"

def test_sovereign_ipc():
    client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    client.connect(SOCKET_PATH)
    
    payload = {
        "x": 98765432,
        "y": 23456789,
        "text": "PI.DEV:IPC_SOVEREIGN_TEST_ACTIVE"
    }
    data = pickle.dumps(payload)
    
    start = time.time()
    client.sendall(struct.pack("!I", len(data)) + data)
    
    raw_len = client.recv(4)
    length = struct.unpack("!I", raw_len)[0]
    response_data = client.recv(length)
    result = pickle.loads(response_data)
    elapsed = (time.time() - start) * 1000
    
    client.close()
    print(f"[ok] Sovereign IPC round-trip complete in {elapsed:.2f} ms")
    print(f"[ok] Coordinates: {result['coordinates']}")
    print(f"[ok] Payload: {result['payload']}")
    print(f"[ok] Output Shape: {result['output_shape']}")
    print(f"[ok] Tensor Norm: {result['tensor_norm']:.4f}")

if __name__ == "__main__":
    test_sovereign_ipc()
