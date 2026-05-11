from scanners.base import BaseScanner
import os
import xml.etree.ElementTree as ET

class NmapScanner(BaseScanner):
    async def run(self):
        output_file = os.path.join(self.output_dir, "nmap.xml")
        # -sV: service version detection, -T2: more conservative/memory-stable
        command = f"nmap -sV -T2 -oX {output_file} {self.target}"
        stdout, stderr, code = await self.execute_command(command)
        
        results = []
        if os.path.exists(output_file):
            tree = ET.parse(output_file)
            root = tree.getroot()
            for host in root.findall('host'):
                ip = host.find('address').get('addr')
                for port in host.find('ports').findall('port'):
                    port_id = port.get('portid')
                    protocol = port.get('protocol')
                    state = port.find('state').get('state')
                    service = port.find('service').get('name') if port.find('service') is not None else "unknown"
                    version = port.find('service').get('product') if port.find('service') is not None else ""
                    results.append({
                        "ip": ip,
                        "port": int(port_id),
                        "protocol": protocol,
                        "state": state,
                        "service": service,
                        "version": version
                    })
        
        return results
