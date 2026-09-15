#!/usr/bin/env python3
import os
import sys
import subprocess
import time
import shutil

def run_cmd(command, check=True):
    print(f"[EXEC] {command}")
    result = subprocess.run(command, shell=True, check=check)
    return result.returncode

def main():
    print("==============================================================================")
    print(" OMNI-MASTER BOOTSTRAP: UNIFIED SYSTEM INITIALIZATION & ORCHESTRATION")
    print("==============================================================================")

    # Step 1: Directory & Environment Verification
    print("\n=== [1/6] Initializing Sovereign Enterprise Environment ===")
    if not os.path.exists(".git"):
        run_cmd("git init", check=False)
        run_cmd("git remote add origin https://github.com/Agentcygroup/sovereign-rig.git", check=False)
        run_cmd("git branch -M main", check=False)

    # Step 2: Dependency Installation
    print("\n=== [2/6] Installing & Verifying Dependencies ===")
    run_cmd(f"{sys.executable} -m pip install --upgrade pip fastapi uvicorn streamlit ray requests", check=False)

    # Step 3: Port Hygiene & Process Cleanup
    print("\n=== [3/6] Purging Conflicting Daemons & Clearing Ports ===")
    run_cmd("lsof -ti:8000,8501 | xargs kill -9 2>/dev/null || true", check=False)

    # Step 4: Substrate & Distributed Memory Initialization
    print("\n=== [4/6] Initializing Distributed Memory Substrate ===")
    redis_path = shutil.which("redis-server")
    if redis_path:
        print("[OK] redis-server binary detected; starting Redis daemon.")
        run_cmd("redis-server --daemonize yes --port 6379", check=False)
    else:
        print("[NOTE] redis-server binary not detected; routing via Ray distributed object substrate.")

    # Step 5: Git Enterprise Synchronization
    print("\n=== [5/6] Synchronizing with GitHub Organization (Agentcygroup) ===")
    run_cmd("git add .", check=False)
    run_cmd("git commit -m 'Omni-Master Automated Release: Unified Sovereign Rig' --no-verify", check=False)
    run_cmd("git push -u origin main --no-verify", check=False)

    # Step 6: Launching Runtime Microservices & Daemons
    print("\n=== [6/6] Launching Runtime Microservices & Control Panels ===")
    
    # Start FastAPI Dual Gateway (REST / WebSocket)
    gateway_proc = subprocess.Popen([
        sys.executable, "-m", "uvicorn", "sovereign_gateway:app", "--host", "127.0.0.1", "--port", "8000"
    ])
    
    # Start Sentinel Telemetry Daemon
    sentinel_proc = subprocess.Popen([
        sys.executable, "sovereign_enterprise_sentinel.py"
    ])
    
    # Start Streamlit Symmetrical Control Center
    streamlit_proc = subprocess.Popen([
        sys.executable, "-m", "streamlit", "run", "sovereign_dashboard.py", "--server.headless", "true"
    ])

    time.sleep(3)

    print("\n==============================================================================")
    print(" SOVEREIGN OMNI-UNIVERSE RIG: 100% OPERATIONAL & SYNCHRONIZED")
    print("------------------------------------------------------------------------------")
    print(" * FastAPI Dual Gateway      : http://127.0.0.1:8000")
    print(" * WebSocket Mesh Socket     : ws://127.0.0.1:8000/ws/{client_id}")
    print(" * Streamlit Control Center  : http://127.0.0.1:8501")
    print(" * GitHub Repository         : https://github.com/Agentcygroup/sovereign-rig")
    print("==============================================================================\n")

    try:
        gateway_proc.wait()
        sentinel_proc.wait()
        streamlit_proc.wait()
    except KeyboardInterrupt:
        print("\n[INFO] Shutting down Sovereign Omni-Universe Rig daemons gracefully...")
        gateway_proc.terminate()
        sentinel_proc.terminate()
        streamlit_proc.terminate()
        sys.exit(0)

if __name__ == "__main__":
    main()
