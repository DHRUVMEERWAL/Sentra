import pandas as pd
import numpy as np
from typing import List, Dict, Any
from loguru import logger
from collections import Counter

class FeatureExtractor:
    def __init__(self):
        pass

    def extract_features(self, packets: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Convert a list of raw packet dicts into a DataFrame of features,
        aggregated by Source IP (Device).
        """
        if not packets:
            return pd.DataFrame()

        df = pd.DataFrame(packets)
        
        # Ensure numeric columns
        df['size'] = pd.to_numeric(df['size'], errors='coerce').fillna(0)
        
        # Group by Source IP (The Device)
        grouped = df.groupby('src_ip')
        
        features_list = []
        
        for src_ip, group in grouped:
            feat = {}
            feat['device_ip'] = src_ip
            
            # Volume
            feat['packet_count'] = len(group)
            feat['bytes_total'] = group['size'].sum()
            feat['bytes_avg'] = group['size'].mean()
            
            # Diversity
            feat['unique_dst_ips'] = group['dst_ip'].nunique()
            feat['unique_dst_ports'] = group['dst_port'].nunique()
            
            # Protocols
            proto_counts = group['proto_name'].value_counts(normalize=True)
            feat['proto_tcp_ratio'] = proto_counts.get('TCP', 0.0)
            feat['proto_udp_ratio'] = proto_counts.get('UDP', 0.0)
            
            # Specific Vulnerable Ports (Dynamic Discovery)
            # We track these specifically so the model learns "RTSP Floods" vs "Web Browsing"
            feat['port_554_count'] = group['dst_port'].apply(lambda x: 1 if x == 554 else 0).sum()
            feat['port_80_count'] = group['dst_port'].apply(lambda x: 1 if x == 80 else 0).sum()
            feat['port_22_count'] = group['dst_port'].apply(lambda x: 1 if x == 22 else 0).sum()
            
            # Reserved Ports (< 1024) Ratio
            reserved_count = group['dst_port'].apply(lambda x: 1 if x < 1024 else 0).sum()
            feat['reserved_port_ratio'] = reserved_count / len(group)

            # Flags (Scan detection)
            # Check for SYN only (naive check)
            if 'flags' in group.columns:
                # Scapy flags are strings like 'S', 'PA', etc.
                syn_count = group['flags'].apply(lambda x: 'S' in str(x) and 'A' not in str(x)).sum()
                feat['syn_count'] = syn_count
                feat['syn_ratio'] = syn_count / len(group)
            else:
                feat['syn_count'] = 0
                feat['syn_ratio'] = 0.0

            features_list.append(feat)
            
        return pd.DataFrame(features_list).set_index('device_ip')

if __name__ == "__main__":
    # Test
    sample = [
        {"src_ip": "10.0.0.1", "dst_ip": "8.8.8.8", "size": 100, "proto_name": "TCP", "dst_port": 80, "flags": "S"},
        {"src_ip": "10.0.0.1", "dst_ip": "8.8.8.8", "size": 100, "proto_name": "TCP", "dst_port": 443, "flags": "S"},
        {"src_ip": "10.0.0.2", "dst_ip": "1.1.1.1", "size": 500, "proto_name": "UDP", "dst_port": 53, "flags": ""},
    ]
    fe = FeatureExtractor()
    print(fe.extract_features(sample))
