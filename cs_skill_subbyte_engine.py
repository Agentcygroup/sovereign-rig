import torch
import math
import time
from sparse_engine import SparseLinearAttentionRouter

class CSSkillSubByteEngine:
    """
    Maps every logical byte into 256 sub-bytes anchored to mathematical constants (pi, e)
    and routes them through a sparse expert matrix representing comprehensive Computer Science domains.
    """
    def __init__(self):
        self.device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
        self.router = SparseLinearAttentionRouter(input_dim=256, hidden_dim=512, num_experts=16, top_k=4).to(self.device)
        self.router.eval()
        
        # Mathematical scaling anchors for universal CS domain mapping
        self.pi_anchor = math.pi
        self.e_anchor = math.e
        
        # Core Computer Science skill domains mapped to expert indices
        self.cs_domains = {
            0: "Distributed Systems & Consensus",
            1: "Compilers & Static Analysis",
            2: "Cryptography & Zero-Knowledge Proofs",
            3: "Operating Systems & Memory Management",
            4: "Computer Vision & Spatial Compute",
            5: "Network Architecture & Routing",
            6: "Database Engines & Storage",
            7: "Hardware Acceleration & Metal Shaders"
        }

    def encode_byte_to_subbytes(self, byte_val: int) -> torch.Tensor:
        """
        Transforms a single byte (0-255) into 256 sub-bytes using pi/e modulation
        to form a high-dimensional dense feature vector for sparse routing.
        """
        indices = torch.arange(256, dtype=torch.float32, device=self.device)
        # Deterministic sub-byte expansion anchored to mathematical constants
        sub_bytes = torch.sin(indices * (self.pi_anchor / 256.0) + (byte_val * self.e_anchor / 256.0))
        return sub_bytes.reshape(1, 1, 256)

    def process_symbolic_stream(self, data_stream: bytes) -> dict:
        start = time.time()
        activations = []
        
        with torch.no_grad():
            for b in data_stream:
                sub_byte_tensor = self.encode_byte_to_subbytes(b)
                routed_output = self.router(sub_byte_tensor)
                activations.append(routed_output.cpu())
                
        stacked = torch.cat(activations, dim=1)
        elapsed = (time.time() - start) * 1000
        
        return {
            "stream_length": len(data_stream),
            "output_shape": stacked.shape,
            "latency_ms": elapsed,
            "tensor_norm": stacked.norm().item()
        }

if __name__ == "__main__":
    engine = CSSkillSubByteEngine()
    # Test stream covering all foundational CS payload symbols
    test_payload = b"PI.DEV:SYSTEM_READY:CS_ALL_SKILLS_ACTIVE"
    
    result = engine.process_symbolic_stream(test_payload)
    print(f"[ok] Processed {result['stream_length']} bytes into 256 sub-byte vectors in {result['latency_ms']:.2f} ms")
    print(f"[ok] Consolidated Tensor Shape: {result['output_shape']}")
    print(f"[ok] Consolidated Tensor Norm: {result['tensor_norm']:.4f}")
