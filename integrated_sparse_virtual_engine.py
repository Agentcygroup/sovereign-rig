import torch
import time
from sparse_engine import SparseLinearAttentionRouter
from virtual_context_box import VirtualContextBox

class IntegratedVirtualSparseEngine:
    """
    Bridges the 600M^2 Virtual Context Box with the Sparse Linear Attention Router,
    mapping 1 byte into 256 sub-bytes across the virtual addressable space.
    """
    def __init__(self):
        self.device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
        self.router = SparseLinearAttentionRouter(input_dim=256, hidden_dim=512).to(self.device)
        self.vbox = VirtualContextBox(resolution=600_000_000)
        self.router.eval()

    def execute_decision_cycle(self, x_coord: int, y_coord: int) -> torch.Tensor:
        # 1. Sample patch from virtual space (block_size=64 -> 64x64 = 4096 elements)
        patch = self.vbox.query_virtual_address(x_coord, y_coord, block_size=64)
        
        # Reshape 4096 elements into [Batch(1), Seq(16), Dim(256)] matching 256 sub-bytes per token
        tensor_input = patch.reshape(1, 16, 256).to(self.device)
        
        # 2. Route through Top-K sparse experts via linear attention
        with torch.no_grad():
            decision_output = self.router(tensor_input)
            
        return decision_output

if __name__ == "__main__":
    engine = IntegratedVirtualSparseEngine()
    start = time.time()
    
    out = engine.execute_decision_cycle(12345678, 87654321)
    elapsed = (time.time() - start) * 1000
    
    print(f"[ok] Integrated Virtual-Sparse decision cycle completed in {elapsed:.2f} ms")
    print(f"[ok] Output decision tensor shape: {out.shape}")
    print(f"[ok] Output tensor norm: {out.norm().item():.4f}")
