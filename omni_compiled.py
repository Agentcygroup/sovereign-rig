import torch
import ray

class CustomRuntime(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.conv = torch.nn.Conv2d(3, 16, kernel_size=3, padding=1)
        self.act = torch.nn.SiLU()

    def forward(self, x):
        return self.act(self.conv(x))

@ray.remote
class CompiledWorkerNode:
    def __init__(self, node_id: int):
        self.node_id = node_id
        self.device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
        base = CustomRuntime().to(self.device).eval()
        self.compiled = torch.compile(base, mode="reduce-overhead")
        self.compiled(torch.randn(1, 3, 256, 256, device=self.device))

    def execute(self, data: list):
        tensor = torch.tensor(data, dtype=torch.float32, device=self.device)
        with torch.inference_mode():
            out = self.compiled(tensor)
        return {"node": self.node_id, "checksum": float(out.sum().item()), "status": "COMPILED_OK"}

if __name__ == "__main__":
    if not ray.is_initialized():
        ray.init(ignore_reinit_error=True)
    worker = CompiledWorkerNode.remote(1)
    payload = torch.randn(2, 3, 256, 256).tolist()
    print(ray.get(worker.execute.remote(payload)))
