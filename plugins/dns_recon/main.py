import subprocess
import shlex

class DNSReconPlugin:
    def __init__(self):
        self.name = "dns_recon"
        self.description = "Performs basic DNS reconnaissance using dig."

    def run(self, target):
        try:
            cmd = f"dig +short A {target}"
            result = subprocess.run(shlex.split(cmd), capture_output=True, text=True, timeout=30)
            return result.stdout
        except Exception as e:
            return str(e)

def setup():
    return DNSReconPlugin()
