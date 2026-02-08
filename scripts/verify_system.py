import sys
import os
import time
import numpy as np
import pandas as pd
from loguru import logger

# Add root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    from core.perception.sniffer import NetworkSniffer
    from core.perception.scanner import DeviceScanner
    from core.data.store import PacketStore
    from core.data.features import FeatureExtractor
    from core.data.slm import SLMCompactor
    from core.analysis.reduction import DimReducer
    from core.analysis.ensemble import AnomalyEnsemble
    from core.analysis.builder import EventBuilder
    from core.agent.brain import SentraAgent
except ImportError as e:
    logger.error(f"Import failed: {e}")
    sys.exit(1)

def generate_traffic(n=5):
    """Generates a sequence of mock packets."""
    for i in range(n):
        # Normal Traffic
        yield {
            "timestamp": time.time(), 
            "src_ip": "10.0.0.5", 
            "dst_ip": "8.8.8.8", 
            "size": np.random.randint(64, 1500), 
            "protocol": 6, 
            "src_port": np.random.randint(1024, 65535), 
            "dst_port": 443, 
            "flags": "PA", 
            "proto_name": "TCP"
        }
    
    # Attack Traffic
    yield {
        "timestamp": time.time(), 
        "src_ip": "10.0.0.5", 
        "dst_ip": "192.168.1.50", 
        "size": 5000, 
        "protocol": 6, 
        "src_port": 5555, 
        "dst_port": 445, 
        "flags": "S", 
        "proto_name": "TCP"
    }

def run_verification():
    logger.info("=== Starting Live Sentra Core Verification ===")
    
    # 1. Init System
    slm = SLMCompactor()
    fe = FeatureExtractor()
    ensemble = AnomalyEnsemble(contamination=0.1)
    builder = EventBuilder(threshold=3.0) # Adjusted threshold
    agent = SentraAgent()
    
    # Mock Training
    logger.info("Training models on baseline data...")
    X_train = np.random.rand(100, 5) # Mock reduced features
    Seq_train = np.random.rand(100, 10, 5) # Mock sequence
    ensemble.fit(X_train, Seq_train)
    
    logger.info("Starting Traffic Loop...")
    
    buffer = []
    
    for i, packet in enumerate(generate_traffic(n=20)):
        logger.info(f"\n--- Packet {i+1} ---")
        logger.debug(f"RAW PACKET: {packet}")
        
        # Buffer for SLM aggregation (simulating window)
        buffer.append(packet)
        
        if len(buffer) >= 5:
            # unique src_ips
            logger.info(f"Processing Window of {len(buffer)} packets...")
            
            # SLM
            compacted = slm.compact(buffer)
            
            # Features
            features_df = fe.extract_features(buffer)
            if features_df.empty:
                continue
                
            # Reduce (Mock for verify script since we don't have fitted reducer persistence yet here easily)
            # In real app, reducer is fitted once. Here we just mock correct shape.
            X_input = np.random.rand(len(features_df), 5) 
            Seq_input = np.random.rand(len(features_df), 10, 5)
            
            # Score
            scores_dict = ensemble.score(X_input, Seq_input)
            agg_score = scores_dict['aggregate'][0] # Take first for demo
            
            logger.info(f"Anomaly Score: {agg_score:.4f}")
            
            # Event
            event = builder.build_event(packet['src_ip'], scores_dict)
            
            if event:
                logger.warning(f"!!! SECURITY EVENT GENERATED !!! Severity: {event['severity']}")
                logger.info("Engaging Agent...")
                decision = agent.run(event)
                logger.success(f"AGENT ACTION: {decision['intent']}")
            else:
                logger.info("Status: Normal")
            
            buffer = [] # Clear buffer
            time.sleep(0.5)

    logger.success("=== Verification Loop Complete ===")

if __name__ == "__main__":
    run_verification()
