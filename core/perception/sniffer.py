import asyncio
import time
from typing import Dict, Any, Optional
from scapy.all import sniff, IP, TCP, UDP
from scapy.packet import Packet
from loguru import logger
import threading
import queue

class NetworkSniffer:
    def __init__(self, interface: str = "en0", store_queue: Optional[queue.Queue] = None):
        """
        Initialize the Network Sniffer.
        
        Args:
            interface: Network interface to sniff on (e.g., 'en0', 'eth0').
            store_queue: Thread-safe queue to push parsed metadata to.
        """
        self.interface = interface
        self.queue = store_queue if store_queue else queue.Queue()
        self.running = False
        self.thread = None

    def _parse_packet(self, packet: Packet) -> Optional[Dict[str, Any]]:
        """
        Extract structured metadata from a raw packet.
        """
        try:
            if not packet.haslayer(IP):
                return None

            metadata = {
                "timestamp": packet.time,
                "src_ip": packet[IP].src,
                "dst_ip": packet[IP].dst,
                "size": len(packet),
                "protocol": packet[IP].proto, # 6 for TCP, 17 for UDP
            }

            if packet.haslayer(TCP):
                metadata.update({
                    "src_port": packet[TCP].sport,
                    "dst_port": packet[TCP].dport,
                    "flags": str(packet[TCP].flags),
                    "proto_name": "TCP"
                })
            elif packet.haslayer(UDP):
                metadata.update({
                    "src_port": packet[UDP].sport,
                    "dst_port": packet[UDP].dport,
                    "proto_name": "UDP"
                })
            else:
                metadata["proto_name"] = "OTHER"

            return metadata

        except Exception as e:
            logger.error(f"Error parsing packet: {e}")
            return None

    def _sniff_loop(self):
        """
        Blocking sniff loop to be run in a separate thread.
        """
        logger.info(f"Starting Scapy Sniffer on {self.interface}...")
        
        def process_packet(packet):
            if not self.running:
                return True # Stop sniffing
            
            data = self._parse_packet(packet)
            if data:
                self.queue.put(data)

        # store=0 to avoid keeping packets in memory
        sniff(iface=self.interface, prn=process_packet, store=0, stop_filter=lambda x: not self.running)
        logger.info("Sniffer stopped.")

    def start(self):
        """
        Start the sniffer in a background thread.
        """
        if self.running:
            logger.warning("Sniffer is already running.")
            return

        self.running = True
        self.thread = threading.Thread(target=self._sniff_loop, daemon=True)
        self.thread.start()

    def stop(self):
        """
        Stop the sniffer.
        """
        logger.info("Stopping sniffer...")
        self.running = False
        if self.thread:
            self.thread.join(timeout=2.0)

if __name__ == "__main__":
    # Test harness
    q = queue.Queue()
    sniffer = NetworkSniffer(interface="en0", store_queue=q)
    sniffer.start()
    
    try:
        print("Sniffer running... Press Ctrl+C to stop.")
        while True:
            try:
                data = q.get(timeout=1)
                print(f"Captured: {data}")
            except queue.Empty:
                pass
    except KeyboardInterrupt:
        sniffer.stop()
