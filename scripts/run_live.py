import sys
import os
import time
import queue
import signal
from loguru import logger
import numpy as np
import pandas as pd

# Add root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.perception.sniffer import NetworkSniffer
from core.data.store import PacketStore
from core.data.features import FeatureExtractor
from core.data.slm import SLMCompactor
from core.analysis.ensemble import AnomalyEnsemble
from core.analysis.builder import EventBuilder
from core.agent.brain import SentraAgent

# Global flag for graceful shutdown
RUNNING = True

def handle_signal(sig, frame):
    global RUNNING
    logger.info("Stopping Live Monitor...")
    RUNNING = False

signal.signal(signal.SIGINT, handle_signal)

def run_live():
    if os.geteuid() != 0:
        logger.error("You must run this script as root (sudo) to capture packets on macOS!")
        sys.exit(1)

    logger.info("=== SENTRA LIVE MONITOR (Listening on en0) ===")
    
    # 1. Initialize Pipeline
    # Using 'en0' (Physical LAN) to capture traffic from Docker VM targeting Host IP
    packet_queue = queue.Queue()
    sniffer = NetworkSniffer(interface="en0", store_queue=packet_queue) 
    
    # Store & Features
    # store = PacketStore("live_data.db")
    slm = SLMCompactor()
    fe = FeatureExtractor()
    
    # Brain (ML)
    # Note: In a real system, we'd load a pre-trained model. 
    # Here, we will Online Train (Learn) on the first 30 seconds of traffic, then Switch to Predict (Defend).
    ensemble = AnomalyEnsemble(contamination=0.05)
    
    # Agent
    builder = EventBuilder(threshold=2.5) # Tuning threshold for demo
    agent = SentraAgent()
    
    # 2. Start Sniffing
    sniffer.start()
    
    # 3. Processing Loop
    logger.info("Waiting for traffic... (Generate traffic using the Docker Simulation)")
    
    buffer = []
    training_data = []      # To hold initial "normal" traffic
    is_training_mode = True
    start_time = time.time()
    TRAINING_DURATION = 45 # seconds
    
    while RUNNING:
        try:
            # Drain queue into buffer
            while not packet_queue.empty():
                pkt = packet_queue.get_nowait()
                # Filter related ports (5554 is our RTSP map, 8081 is HTTP map)
                if pkt.get('dst_port') in [5554, 8081] or pkt.get('src_port') in [5554, 8081]:
                    buffer.append(pkt)
            
            if len(buffer) >= 5: # Process batches
                logger.debug(f"Processing batch of {len(buffer)} packets...")
                
                # 1. Compact
                flows = slm.compact(buffer)
                
                # 2. Extract Features
                features_df = fe.extract_features(buffer) # Extract from raw buffer for better granularity
                
                if features_df.empty:
                    buffer = []
                    continue

                # Prepare input vectors
                # Using a subset of features for the model (Size, proto_ratio, syn_ratio)
                # Just using raw 9-dim features for now, filling NaN
                X = features_df.fillna(0).values
                # Fake sequence dim for LSTM (just repeat X for now or use history)
                # (Samples, Time, Feat) -> (N, 5, F)
                X_seq = np.zeros((X.shape[0], 5, X.shape[1]))
                for i in range(5): X_seq[:, i, :] = X 
                
                if is_training_mode:
                    training_data.append((X, X_seq))
                    elapsed = time.time() - start_time
                    logger.info(f"[LEARNING] Collecting normal baseline... ({int(elapsed)}/{TRAINING_DURATION}s) | Packets: {len(buffer)}")
                    
                    if elapsed > TRAINING_DURATION:
                        logger.success(">>> TRAINING PHASE COMPLETE. TRAINING MODELS... <<<")
                        # Aggregate all training data
                        X_all = np.vstack([t[0] for t in training_data])
                        seq_all = np.vstack([t[1] for t in training_data])
                        
                        if len(X_all) < 10:
                            logger.warning("Not enough data to train! Extending time...")
                            start_time = time.time() - (TRAINING_DURATION - 10)
                        else:
                            ensemble.fit(X_all, seq_all)
                            is_training_mode = False
                            logger.success(">>> SYSTEM ARMED. MONITORING FOR ANOMALIES. <<<")
                
                else:
                    # PREDICTION MODE
                    scores = ensemble.score(X, X_seq)
                    agg_score = scores['aggregate'].mean() # Mean of batch
                    
                    if agg_score > 0.1: # Noisy logs reduction
                        logger.info(f"[DEFENSE] Anomaly Score: {agg_score:.4f} (GMM: {scores['gmm'].mean():.2f})")
                    
                    # Check for Event
                    if agg_score > builder.threshold:
                        target_ip = features_df.index[0] # The device IP
                        event = builder.build_event(target_ip, {"aggregate": float(agg_score)})
                        
                        if event:
                            logger.critical(f"!!! ATTACK DETECTED !!! Severity: {event['severity']}")
                            decision = agent.run(event)
                            logger.critical(f"AGENT RESPONSE: {decision['intent']}")
            
                buffer = [] # Flush
            
            time.sleep(1)
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            logger.error(f"Error in loop: {e}")
            time.sleep(1)

    sniffer.stop()
    logger.info("System Shutdown.")

if __name__ == "__main__":
    run_live()
