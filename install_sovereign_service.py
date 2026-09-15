import os
import plistlib

plist_content = {
    "Label": "com.metadusa.sovereign.gateway",
    "ProgramArguments": ["/Users/metadusa/.pi-venv/bin/python3", "/Users/metadusa/usd-rig/sovereign_gateway.py"],
    "RunAtLoad": True,
    "KeepAlive": True,
    "StandardOutPath": "/Users/metadusa/usd-rig/sovereign_out.log",
    "StandardErrorPath": "/Users/metadusa/usd-rig/sovereign_err.log"
}

plist_path = os.path.expanduser("~/Library/LaunchAgents/com.metadusa.sovereign.gateway.plist")

with open(plist_path, "wb") as f:
    plistlib.dump(plist_content, f)

print(f"[+] Sovereign LaunchAgent written to {plist_path}")
print("[+] To load the service, run: launchctl load ~/Library/LaunchAgents/com.metadusa.sovereign.gateway.plist")
