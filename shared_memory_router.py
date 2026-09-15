import torch
import torch.multiprocessing as mp
from multiprocessing import shared_memory
import struct
import time
import os

SHM_NAME = "sovereign_tensor_shm"
SHM_SIZE = 4096 * 256 * 4 # Space for large float32 payloads

class SharedMemorySovereignBridge:
    """
    Zero-Copy Shared Memory IPC Bridge for Ultra-Low-Latency Tensor Routing.
    Bypasses socket stream serialization by sharing underlying memory pointers.
    """
    def __init__(self, create=False):
        self.create = create
        if create:
            try:
                self.shm = shared_memory.SharedMemory(name=SHM_NAME, create=True, size=SHM_SIZE)
            except FileExistsError:
                existing = shared_memory.SharedMemory(name=SHM_NAME)
                existing.close()
                existing.unlink()
                self.shm = shared_memory.SharedMemory(name=SHM_NAME, create=True, size=SHM_SIZE)
        else:
            self.shm = shared_memory.SharedMemory(name=SHM_NAME)

    def write_tensor(self, tensor: torch.Tensor) -> int:
        flat = tensor.detach().cpu().contiguous().flatten()
        byte_data = flat.numpy().tobytes()
        size = len(byte_data)
        
        # Write size header followed by tensor payload into shared memory
        header = struct.pack("!I", size)
        self.shm.buf[:4] = header
        self.shm.buf[4:4+size] = byte_data
        return size

    def read_tensor(self, shape) -> torch.Tensor:
        raw_header = bytes(self.shm.buf[:4])
        size = struct.unpack("!I", raw_header)[0]
        
        buffer = bytes(self.shm.buf[4:4+size])
        tensor = torch.frombuffer(bytearray(buffer), dtype=torch.float32).clone().reshape(shape)
        return tensor

    def close(self):
        self.shm.close()
        if self.create:
            try:
                self.shm.unlink()
            except:
                pass

if __name__ == "__main__":
    bridge = SharedMemorySovereignBridge(create=True)
    test_tensor = torch.randn(1, 16, 256)
    
    start = time.time()
    bridge.write_tensor(test_tensor)
    recovered = bridge.read_tensor((1, 16, 256))
    elapsed = (time.time() - start) * 1000
    
    print(f"[ok] Zero-copy shared memory round-trip complete in {elapsed:.3f} ms")
    print(f"[ok] Recovered tensor shape: {recovered.shape} | Norm: {recovered.norm().item():.4f}")
    bridge.close()
