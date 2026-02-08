import nmap
import json
from typing import List, Dict, Any
from loguru import logger
import socket
import netifaces

class DeviceScanner:
    def __init__(self, subnet: str = None):
        """
        Initialize the Device Scanner.
        
        Args:
            subnet: CIDR to scan (e.g., '192.168.1.0/24'). If None, tries to detect.
        """
        self.nm = nmap.PortScanner()
        self.subnet = subnet or self._detect_subnet()

    def _detect_subnet(self) -> str:
        """
        Attempt to detect the local subnet.
        """
        try:
            # simple heuristic: get default gateway interface IP
            gws = netifaces.gateways()
            default_gw = gws.get('default', {}).get(netifaces.AF_INET)
            if default_gw:
                iface = default_gw[1]
                addrs = netifaces.ifaddresses(iface)
                ip_info = addrs[netifaces.AF_INET][0]
                ip = ip_info['addr']
                # Assume /24 for now for home networks
                return f"{ip.rsplit('.', 1)[0]}.0/24"
        except Exception as e:
            logger.error(f"Could not detect subnet: {e}")
        return "127.0.0.1/32" # Fallback

    def scan_network_sweep(self) -> List[Dict[str, Any]]:
        """
        Perform a ping sweep to find active hosts.
        """
        logger.info(f"Starting ping sweep on {self.subnet}...")
        try:
            # -sn: Ping Scan - disable port scan
            self.nm.scan(hosts=self.subnet, arguments='-sn')
            hosts = []
            for host in self.nm.all_hosts():
                hosts.append({
                    "ip": host,
                    "status": self.nm[host].state(),
                    "hostname": self.nm[host].hostname()
                })
            logger.info(f"Found {len(hosts)} active hosts.")
            return hosts
        except Exception as e:
            logger.error(f"Scan failed: {e}")
            return []

    def scan_device_details(self, ip: str) -> Dict[str, Any]:
        """
        Deep scan of a specific IP for OS, services, and ports.
        """
        logger.info(f"Deep scanning {ip}...")
        try:
            # -sS: SYN scan, -O: OS detection (needs root usually, maybe drop -O if no sudo)
            # We'll stick to -sV for version detection which is safer/easier
            self.nm.scan(hosts=ip, arguments='-sV -T4')
            if ip not in self.nm.all_hosts():
                return {}
            
            data = self.nm[ip]
            # Convert to dict safely
            return {
                "ip": ip,
                "hostnames": data.get("hostnames", []),
                "protocols": list(data.keys()),
                "tcp_ports": data.get("tcp", {}),
                "udp_ports": data.get("udp", {}),
            }
        except Exception as e:
            logger.error(f"Deep scan failed for {ip}: {e}")
            return {}

if __name__ == "__main__":
    scanner = DeviceScanner()
    print(f"Detected Subnet: {scanner.subnet}")
    hosts = scanner.scan_network_sweep()
    print(f"Hosts: {json.dumps(hosts, indent=2)}")
    
    if hosts:
        target = hosts[0]['ip']
        details = scanner.scan_device_details(target)
        print(f"Details for {target}: {json.dumps(details, indent=2)}")
