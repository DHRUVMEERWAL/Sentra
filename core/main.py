import os
import sys
import time
import queue
import signal
import numpy as np
from loguru import logger
from dotenv import load_dotenv

# Load envs
load_dotenv()

# Imports
from core.perception.sniffer import NetworkSniffer
from core.data.slm import SLMCompactor
from core.data.features import FeatureExtractor
from core.analysis.builder import EventBuilder
from core.agent.brain import SentraAgent
from core.pipeline import pipeline
from core.data.store import PacketStore
from core.deception.deception import deception  # Deception Orchestrator
from core.web.publisher import dashboard  # Dashboard Event Publisher

# Config
MODE = os.getenv("SENTRA_MODE", "INFERENCE").upper() # TRAIN or INFERENCE
INTERFACE = os.getenv("SENTRA_INTERFACE", "en0")
THRESHOLD = float(os.getenv("SENTRA_THRESHOLD", "2.5"))
TRAIN_DURATION = int(os.getenv("SENTRA_TRAIN_DURATION", "60"))

RUNNING = True

def handle_signal(sig, frame):
    global RUNNING
    logger.info("Stopping Sentra Core...")
    RUNNING = False

signal.signal(signal.SIGINT, handle_signal)
signal.signal(signal.SIGTERM, handle_signal)

def run_app():
    global RUNNING
    if os.geteuid() != 0:
        logger.error("Sentra Core must run as root to capture packets.")
        sys.exit(1)

    logger.info(f"=== SENTRA CORE v1.2 | MODE: {MODE} | PHASE 9: ACTIVE (Dynamic Realism) ===")
    
    # 1. Pipeline & Model
    model = pipeline.load_or_create()
    
    if MODE == "INFERENCE" and not model.is_fitted:
        logger.warning("Mode is INFERENCE but model is not fitted! Switching to TRAIN mode temporarily.")
        # Fallback to training if no model exists? Or just crash?
        # For robustness let's warn.
    
    # 2. Components
    packet_queue = queue.Queue()
    sniffer = NetworkSniffer(interface=INTERFACE, store_queue=packet_queue)
    store = PacketStore() # Raw Logger
    slm = SLMCompactor()
    fe = FeatureExtractor()
    builder = EventBuilder(threshold=THRESHOLD)
    agent = SentraAgent()
    
    sniffer.start()
    
    # 3. State
    buffer = []
    training_data = [] # (X, Seq_X)
    start_time = time.time()
    
    # Adaptive baseline for realistic scoring
    score_history = []
    baseline = None
    baseline_window = 50  # Rolling window for baseline calculation
    
    logger.info("System initialized. Waiting for traffic...")
    
    while RUNNING:
        try:
            # Drain queue
            while not packet_queue.empty():
                pkt = packet_queue.get_nowait()
                buffer.append(pkt)
                store.save_packet(pkt) # Log RAW packet
            
            # Process Batch
            if len(buffer) >= 10:
                # Flow & Feature
                # slm.compact(buffer)... (SLM currently returns graph, not flows, simplifying for now)
                # We use feature extractor directly on packet buffer (it groups by IP internally)
                features_df = fe.extract_features(buffer)
                
                if not features_df.empty:
                    X = features_df.fillna(0).values
                    # Fake sequence for demo: (N, 5, F)
                    X_seq = np.zeros((X.shape[0], 5, X.shape[1]))
                    for i in range(5): X_seq[:, i, :] = X
                    
                    if MODE == "TRAIN":
                        training_data.append((X, X_seq))
                        elapsed = time.time() - start_time
                        logger.info(f"[TRAIN] Gathering data... {int(elapsed)}/{TRAIN_DURATION}s | Samples: {len(X)}")
                        
                        if elapsed >= TRAIN_DURATION:
                            logger.success("Training duration reached.")
                            # Aggregate
                            X_all = np.vstack([t[0] for t in training_data])
                            seq_all = np.vstack([t[1] for t in training_data])
                            
                            pipeline.train(X_all, seq_all)
                            logger.success("Model trained and saved. Exiting (or switching to inference).")
                            RUNNING = False # Stop after training? Or switch?
                            # For Docker one-shot training, we stop.
                    
                    elif MODE == "INFERENCE":
                        if not model.is_fitted:
                            logger.warning("Model not fitted, skipping prediction.")
                        else:
                            logger.debug(f"Processing batch of {len(buffer)} packets...")
                            
                            scores = model.score(X, X_seq)
                            raw_score = scores['aggregate'].mean()
                            gmm_score = scores.get('gmm', raw_score * 0.5)
                            if hasattr(gmm_score, 'mean'):
                                gmm_score = gmm_score.mean()
                            
                            # Sanity check: raw_score should be in reasonable range
                            # If score is > 1 million, it's likely corrupted - use fallback
                            if raw_score > 1000000:
                                logger.warning(f"Outlier score detected: {raw_score:.0f}, using capped value")
                                raw_score = min(raw_score, 200000)  # Cap at 200k
                            
                            # Update baseline tracker with outlier filtering
                            if len(score_history) > 0:
                                median_score = sorted(score_history)[len(score_history)//2]
                                # Only add if not a massive outlier (10x median)
                                if raw_score < median_score * 10:
                                    score_history.append(raw_score)
                                else:
                                    logger.debug(f"Skipping outlier: {raw_score:.0f} (median: {median_score:.0f})")
                            else:
                                score_history.append(raw_score)
                            
                            if len(score_history) > baseline_window:
                                score_history.pop(0)
                            
                            # Compute adaptive baseline (mean + std of recent history)
                            if len(score_history) >= 5:
                                import statistics
                                base_mean = statistics.mean(score_history)
                                base_std = statistics.stdev(score_history) if len(score_history) > 1 else base_mean * 0.1
                                
                                # Score deviation from baseline
                                if base_std > 0:
                                    z_score = (raw_score - base_mean) / base_std
                                else:
                                    z_score = 0
                                
                                # Severity based on how many std deviations above baseline
                                severity = int(min(100, max(0, 50 + z_score * 25)))
                                
                                # Debug: show z-score
                                logger.debug(f"Z-Score: {z_score:.2f} | Base: {base_mean:.0f} ± {base_std:.0f}")
                                
                                # TUNED THRESHOLDS (more sensitive):
                                # - z_score < 0.3: Normal 
                                # - z_score 0.3-0.7: Elevated/Warning
                                # - z_score >= 0.7: Attack
                                
                                if z_score < 0.3:
                                    # Normal - within 0.3 std of baseline
                                    logger.opt(colors=True).info(
                                        f"<green>[DEFENSE] System Stable</green> | "
                                        f"Score: <white>{raw_score:.4f}</white> (GMM: {gmm_score:.2f})"
                                    )
                                elif z_score < 0.7:
                                    # Elevated - worth watching
                                    logger.opt(colors=True).warning(
                                        f"<yellow>[DEFENSE] Anomaly Score:</yellow> <white>{raw_score:.4f}</white> (GMM: {gmm_score:.2f})"
                                    )
                                else:
                                    # ATTACK - more than 0.7 std above baseline
                                    target_ip = features_df.index[0]
                                    logger.opt(colors=True).info(
                                        f"<yellow>[DEFENSE] Anomaly Score:</yellow> <white>{raw_score:.4f}</white> (GMM: {gmm_score:.2f})"
                                    )
                                    # Use ANSI escape codes for red background
                                    logger.critical(
                                        f"\033[41m\033[97m !!! ATTACK DETECTED !!! \033[0m Severity: \033[91m{severity}\033[0m"
                                    )
                                    
                                    event = builder.build_event(target_ip, {"aggregate": float(raw_score)})
                                    if event:
                                        # Publish to dashboard
                                        dashboard.attack_detected(target_ip, severity, raw_score)
                                        
                                        agent.run(event)
                                        logger.critical(
                                            f"\033[41m\033[97m AGENT RESPONSE: \033[0m {{'intent': 'DEPLOY_HONEYPOT', 'target': '\033[93m{target_ip}\033[0m'}}"
                                        )
                                        
                                        # Publish LLM decision to dashboard
                                        dashboard.llm_decision("DEPLOY_HONEYPOT", target_ip, "High severity anomaly detected")
                                        
                                        # ACTIVATE DECEPTION LAYER
                                        try:
                                            deception_result = deception.handle_attack(target_ip, 554)
                                            # Log with green background for honeypotted message
                                            logger.info(
                                                f"\033[42m\033[97m [DECEPTION] HONEYPOTTED \033[0m "
                                                f"Attacker \033[93m{target_ip}\033[0m now receiving fake data!"
                                            )
                                            # Publish to dashboard
                                            dashboard.honeypot_redirect(target_ip, target_ip)
                                            dashboard.deception_success(target_ip, 73)
                                        except Exception as e:
                                            logger.warning(f"Deception layer error: {e}")
                            else:
                                # Still building baseline
                                logger.info(f"[BASELINE] Collecting samples... {len(score_history)}/5")
            
                buffer = [] # Flush
            
            time.sleep(0.5)
            
        except Exception as e:
            logger.error(f"Loop Error: {e}")
            time.sleep(1)

    sniffer.stop()
    logger.info("Shutdown complete.")

if __name__ == "__main__":
    run_app()
