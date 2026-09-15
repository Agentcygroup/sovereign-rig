import socket
import pickle
import struct
import time
import concurrent.futures

SOCKET_PATH = "/tmp/sovereign_runtime.sock"

def send_request(worker_id):
    client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    client.connect(SOCKET_PATH)
    
    payload = {
        "x": 10000000 + worker_id * 12345,
        "y": 80000000 - worker_id * 54321,
        "text": f"PI.DEV:SWARM_WORKER_{worker_id}_ACTIVE"
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
    return elapsed, result['output_shape']

def run_benchmark():
    print("[info] Initiating concurrent sovereign swarm IPC benchmark (16 workers)...")
    start_total = time.time()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=16) as executor:
        futures = [executor.submit(send_request, i) for i in range(16)]
        results = [f.result() for f in futures]
        
    total_elapsed = (time.time() - start_total) * 1000
    latencies = [r[0] for r in results]
    
    print(f"[ok] Swarm benchmark complete in {total_elapsed:.2f} ms total")
    print(f"[ok] Average IPC round-trip: {sum(latencies)/len(latencies):.2f} ms")
    print(f"[ok] Min latency: {min(latencies):.2f} ms | Max latency: {max(latencies):.2f} ms")

if __name__ == "__main__":
    run_benchmark()
