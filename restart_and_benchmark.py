import subprocess
import time
import os
import socket

SOCKET_PATH = "/tmp/sovereign_runtime.sock"

def check_daemon_log():
    log_path = os.path.expanduser("~/.llama/sovereign_daemon.log")
    if os.path.exists(log_path):
        print("[info] Recent daemon logs:")
        with open(log_path, "r") as f:
            lines = f.readlines()
            for line in lines[-10:]:
                print(f"  {line.strip()}")

def main():
    print("[info] Stopping any existing sovereign daemon instances...")
    subprocess.run("pkill -f sovereign_daemon.py", shell=True)
    time.sleep(1)
    
    if os.path.exists(SOCKET_PATH):
        os.unlink(SOCKET_PATH)
        
    print("[info] Spawning sovereign daemon in background...")
    subprocess.Popen(
        ["python3", os.path.expanduser("~/usd-rig/sovereign_daemon.py")],
        stdout=open(os.path.expanduser("~/.llama/sovereign_daemon.log"), "w"),
        stderr=subprocess.STDOUT
    )
    
    # Wait for socket to appear
    print("[info] Waiting for socket initialization...")
    for _ in range(10):
        if os.path.exists(SOCKET_PATH):
            print("[ok] Sovereign socket active!")
            break
        time.sleep(0.5)
    else:
        print("[error] Socket failed to initialize. Log output:")
        check_daemon_log()
        return

    print("[info] Running sovereign swarm benchmark script...")
    subprocess.run(["python3", os.path.expanduser("~/usd-rig/benchmark_sovereign_swarm.py")])

if __name__ == "__main__":
    main()
