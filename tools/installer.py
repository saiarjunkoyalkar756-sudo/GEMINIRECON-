import shutil
import subprocess
import os

TOOLS = [
    "subfinder", "amass", "assetfinder", "findomain",
    "naabu", "rustscan", "nmap",
    "httpx", "httprobe",
    "nuclei", "nikto",
    "ffuf", "feroxbuster", "gobuster", "dirsearch",
    "dnsx", "theHarvester", "recon-ng",
    "gowitness", "whatweb",
    "sqlmap", "xsstrike", "hydra",
    "wireshark", "tcpdump"
]

def check_installation():
    """Checks which tools are installed and returns a report."""
    report = {}
    for tool in TOOLS:
        path = shutil.which(tool)
        report[tool] = {
            "installed": path is not None,
            "path": path
        }
    return report

def verify_and_fix():
    """Verifies installations and alerts if setup.sh needs to run."""
    report = check_installation()
    missing = [t for t, info in report.items() if not info["installed"]]
    
    if missing:
        print(f"Warning: The following tools are missing: {', '.join(missing)}")
        print("Please run 'bash setup.sh' to install them.")
        return False
    
    print("All production tools are verified and ready.")
    return True

if __name__ == "__main__":
    verify_and_fix()
