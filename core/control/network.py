import os
from loguru import logger
import subprocess

class NetworkController:
    def __init__(self, platform="mac"):
        self.platform = platform

    def redirect_traffic(self, attacker_ip: str, target_port: int, honeypot_port: int):
        """
        Redirect traffic from attacker to honeypot.
        """
        logger.info(f"REDIRECTING: {attacker_ip} -> :{target_port} ===> :{honeypot_port} (Honeypot)")
        
        if self.platform == "mac":
            self._mac_pf_redirect(attacker_ip, target_port, honeypot_port)
        elif self.platform == "linux":
            self._linux_iptables_redirect(attacker_ip, target_port, honeypot_port)

    def _mac_pf_redirect(self, src_ip, dst_port, redir_port):
        # Generate PF rule
        rule = f"rdr pass inet proto tcp from {src_ip} to any port {dst_port} -> 127.0.0.1 port {redir_port}"
        logger.info(f"Generated PF Rule: {rule}")
        # Note: writing to /etc/pf.anchors/sentra and reloading usually required
        # subprocess.run(["sudo", "pfctl", "-f", ...])

    def _linux_iptables_redirect(self, src_ip, dst_port, redir_port):
        cmd = f"iptables -t nat -A PREROUTING -s {src_ip} -p tcp --dport {dst_port} -j REDIRECT --to-port {redir_port}"
        logger.info(f"Generated IPTables Command: {cmd}")

if __name__ == "__main__":
    nc = NetworkController(platform="mac")
    nc.redirect_traffic("1.2.3.4", 80, 8080)
