import networkx as nx
import community as community_louvain # python-louvain
from typing import List, Dict, Any
from loguru import logger
import pandas as pd

class SLMCompactor:
    """
    Implements a Smart Local Moving (SLM) - style compaction.
    It builds a graph from packet flows and detects communities (clusters of devices).
    It then reduces the traffic to Inter-Community flows.
    """
    def __init__(self, resolution: float = 1.0):
        self.resolution = resolution

    def compact(self, packets: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not packets:
            return []

        # 1. Build Graph
        G = nx.Graph()
        for p in packets:
            src = p.get('src_ip')
            dst = p.get('dst_ip')
            if src and dst:
                if G.has_edge(src, dst):
                    G[src][dst]['weight'] += 1
                else:
                    G.add_edge(src, dst, weight=1)

        if len(G.nodes) == 0:
            return packets # fallback

        # 2. Detect Communities (SLM / Louvain)
        try:
            partition = community_louvain.best_partition(G, resolution=self.resolution)
        except Exception as e:
            logger.warning(f"Community detection failed, returning raw: {e}")
            return packets

        # 3. Compact Packets
        # We transform individual IP-to-IP packets into Community-to-Community flows
        # This reduces the number of "entities" tracking in the ML model
        
        compacted_flows = {} # Key: (comm_src, comm_dst)
        
        for p in packets:
            src = p.get('src_ip')
            dst = p.get('dst_ip')
            if src and dst and src in partition and dst in partition:
                comm_src = partition[src]
                comm_dst = partition[dst]
                
                key = (comm_src, comm_dst)
                if key not in compacted_flows:
                    compacted_flows[key] = {
                        "src_comm": comm_src,
                        "dst_comm": comm_dst,
                        "packet_count": 0,
                        "bytes": 0,
                        "timestamp": p.get('timestamp') # Keep latest
                    }
                
                compacted_flows[key]['packet_count'] += 1
                compacted_flows[key]['bytes'] += p.get('size', 0)
        
        return list(compacted_flows.values())

if __name__ == "__main__":
    # Test
    packets = [
        {"timestamp": 1, "src_ip": "10.0.0.1", "dst_ip": "10.0.0.2", "size": 100},
        {"timestamp": 2, "src_ip": "10.0.0.2", "dst_ip": "10.0.0.1", "size": 100}, # Comm 0
        {"timestamp": 3, "src_ip": "192.168.1.1", "dst_ip": "192.168.1.20", "size": 500}, # Comm 1
    ]
    slm = SLMCompactor()
    compacted = slm.compact(packets)
    print(compacted)
