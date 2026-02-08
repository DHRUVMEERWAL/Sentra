"""
Deception Layer - Honeypot Management and Fake Packet Injection

This module manages the Cowrie honeypot and implements active deception
by sending fake responses to attackers.
"""

import socket
import random
import threading
from loguru import logger
from typing import Dict, Any

# ANSI Colors for deception logs
GREEN_BG = "\033[42m\033[97m"
RESET = "\033[0m"
YELLOW = "\033[93m"

class HoneypotController:
    """
    Controls the Cowrie honeypot and manages traffic redirection.
    """
    
    def __init__(self, cowrie_host: str = "cowrie", cowrie_ports: Dict[str, int] = None):
        self.cowrie_host = cowrie_host
        self.cowrie_ports = cowrie_ports or {
            "ssh": 2222,
            "telnet": 2223
        }
        self.active_redirects = {}  # {attacker_ip: target_port}
        self._running = False
        
    def is_honeypot_available(self) -> bool:
        """Check if Cowrie honeypot is reachable."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((self.cowrie_host, self.cowrie_ports["ssh"]))
            sock.close()
            return result == 0
        except Exception:
            return False
    
    def redirect_attacker(self, attacker_ip: str, original_port: int) -> bool:
        """
        Redirect an attacker to the honeypot.
        In production, this would use iptables/pf rules.
        For simulation, we just log and track.
        """
        target_hp_port = self.cowrie_ports.get("ssh", 2222)
        
        self.active_redirects[attacker_ip] = {
            "original_port": original_port,
            "honeypot_port": target_hp_port,
            "status": "REDIRECTED"
        }
        
        logger.info(
            f"{GREEN_BG} [DECEPTION] HONEYPOTTED {RESET} "
            f"Attacker {YELLOW}{attacker_ip}{RESET} redirected to Cowrie honeypot"
        )
        
        return True
    
    def get_redirect_status(self, attacker_ip: str) -> Dict[str, Any]:
        """Get the current redirect status for an attacker."""
        return self.active_redirects.get(attacker_ip, {"status": "NOT_REDIRECTED"})


class FakePacketInjector:
    """
    Sends fake/decoy data packets to deceive attackers.
    Injects believable but false information into attacker sessions.
    """
    
    # Fake RTSP responses
    FAKE_RTSP_RESPONSES = [
        b"RTSP/1.0 200 OK\r\nCSeq: 1\r\nServer: Fake-Camera/1.0\r\nSession: FAKE12345\r\n\r\n",
        b"RTSP/1.0 401 Unauthorized\r\nCSeq: 1\r\nWWW-Authenticate: Digest realm=\"FAKE\"\r\n\r\n",
    ]
    
    # Fake SSH banners
    FAKE_SSH_BANNERS = [
        b"SSH-2.0-OpenSSH_7.4p1 Raspberry Pi\r\n",
        b"SSH-2.0-OpenSSH_6.6.1 Ubuntu-2ubuntu2.13\r\n",
        b"SSH-2.0-dropbear_2016.74\r\n",
    ]
    
    # Fake HTTP responses
    FAKE_HTTP_RESPONSES = [
        b"HTTP/1.1 200 OK\r\nServer: Apache/2.4.41\r\nContent-Type: text/html\r\n\r\n<html><body><h1>Fake Camera Portal</h1></body></html>",
        b"HTTP/1.1 403 Forbidden\r\nServer: nginx\r\nContent-Type: text/plain\r\n\r\nAccess Denied",
    ]
    
    def __init__(self):
        self.injection_count = 0
        
    def get_fake_response(self, protocol: str) -> bytes:
        """Get a random fake response for the given protocol."""
        if protocol == "rtsp":
            return random.choice(self.FAKE_RTSP_RESPONSES)
        elif protocol == "ssh":
            return random.choice(self.FAKE_SSH_BANNERS)
        elif protocol == "http":
            return random.choice(self.FAKE_HTTP_RESPONSES)
        else:
            return b"FAKE_RESPONSE_DATA\r\n"
    
    def inject_fake_data(self, attacker_ip: str, protocol: str) -> bool:
        """
        Simulate injecting fake data towards the attacker.
        In production, this would require raw socket access.
        """
        fake_data = self.get_fake_response(protocol)
        self.injection_count += 1
        
        logger.info(
            f"{GREEN_BG} [DECEPTION] FAKE DATA SENT {RESET} "
            f"Sent {len(fake_data)} bytes of fake {protocol.upper()} data to {YELLOW}{attacker_ip}{RESET}"
        )
        
        return True


class DeceptionOrchestrator:
    """
    Main orchestrator for the deception layer.
    Coordinates honeypot redirection and fake packet injection.
    """
    
    def __init__(self):
        self.honeypot = HoneypotController()
        self.injector = FakePacketInjector()
        self.deceived_attackers = set()
        
    def handle_attack(self, attacker_ip: str, target_port: int) -> Dict[str, Any]:
        """
        Handle a detected attack by activating deception measures.
        
        Args:
            attacker_ip: The IP address of the attacker
            target_port: The port being attacked
            
        Returns:
            Status dict with deception results
        """
        result = {
            "attacker": attacker_ip,
            "port": target_port,
            "actions": []
        }
        
        # 1. Redirect to honeypot
        if self.honeypot.redirect_attacker(attacker_ip, target_port):
            result["actions"].append("REDIRECTED_TO_HONEYPOT")
            self.deceived_attackers.add(attacker_ip)
        
        # 2. Determine protocol and inject fake data
        protocol = self._guess_protocol(target_port)
        if self.injector.inject_fake_data(attacker_ip, protocol):
            result["actions"].append(f"INJECTED_FAKE_{protocol.upper()}")
        
        # 3. Log the deception success
        logger.success(
            f"{GREEN_BG} [DECEPTION] SUCCESS {RESET} "
            f"Attacker {YELLOW}{attacker_ip}{RESET} is now receiving fake data!"
        )
        
        result["status"] = "DECEIVED"
        return result
    
    def _guess_protocol(self, port: int) -> str:
        """Guess the protocol based on port number."""
        port_protocols = {
            22: "ssh",
            23: "telnet", 
            80: "http",
            443: "http",
            554: "rtsp",
            8080: "http",
            2222: "ssh",
        }
        return port_protocols.get(port, "http")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get deception statistics."""
        return {
            "deceived_attackers": len(self.deceived_attackers),
            "active_redirects": len(self.honeypot.active_redirects),
            "fake_packets_sent": self.injector.injection_count
        }


# Global instance for use in main.py
deception = DeceptionOrchestrator()


if __name__ == "__main__":
    # Test the deception layer
    logger.info("Testing Deception Layer...")
    
    orch = DeceptionOrchestrator()
    
    # Simulate an attack
    result = orch.handle_attack("192.168.1.100", 554)
    print(f"Deception Result: {result}")
    
    # Check stats
    stats = orch.get_stats()
    print(f"Deception Stats: {stats}")
