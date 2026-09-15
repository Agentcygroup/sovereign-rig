import subprocess
import sys

scripts = [
    "sovereign_harness.py",
    "sovereign_sentinel.py",
    "pi_omni_universe_engine.py",
    "omni_spectrum.py"
]

for script in scripts:
    print(f"\n--- EXECUTING: {script} ---")
    subprocess.run([sys.executable, f"/Users/metadusa/usd-rig/{script}"], check=True)

print("\n[All Sovereign Scripts Executed Successfully]")
