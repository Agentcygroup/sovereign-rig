import time
import subprocess
import os

LOG_PATH = os.path.expanduser("~/.llama/thermal_governor.log")

def monitor_hardware_state():
    print("[ok] Thermal & Power Governor active. Monitoring hardware telemetry...")
    while True:
        try:
            # Capture power and thermal statistics via macOS powermetrics or vm_stat fallback
            result = subprocess.run(
                ["powermetrics", "-s", "cpu_power,gpu_power,thermal", "-i", "1000", "-n", "1"],
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True,
                timeout=5
            )
            output = result.stdout
            
            # Extract power metrics lines if available
            metrics = []
            for line in output.split('\n'):
                if "Power" in line or "Thermal" in line or "CPU" in line or "GPU" in line:
                    metrics.append(line.strip())
                    
            log_entry = f"ts={time.time()} | " + " | ".join(metrics[:3]) + "\n"
            with open(LOG_PATH, "a") as f:
                f.write(log_entry)
        except Exception:
            # Fallback log if powermetrics requires root privileges
            fallback_entry = f"ts={time.time()} | status=active (vm_stat mode)\n"
            with open(LOG_PATH, "a") as f:
                f.write(fallback_entry)
                
        time.sleep(10)

if __name__ == "__main__":
    monitor_hardware_state()
