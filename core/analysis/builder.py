from typing import Dict, Any, Optional
import time
import uuid

class EventBuilder:
    def __init__(self, threshold: float = 0.7):
        """
        Args:
            threshold: Anomaly score threshold (0.0 to 1.0) to trigger an event.
        """
        self.threshold = threshold

    def build_event(self, device_ip: str, scores: Dict[str, float], context: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """
        Analyzes scores and constructs an Event if anomaly is detected.
        """
        agg_score = scores.get("aggregate", 0.0)
        
        # Normalize/Clip aggregate score for logic (assuming heuristic from ensemble typically < 5.0)
        # We treat score > threshold as anomaly.
        
        if agg_score > self.threshold:
            # Create Event
            severity = min(int(agg_score * 100), 100)
            if severity > 100: severity = 100
            
            event = {
                "event_id": str(uuid.uuid4()),
                "event_type": "ANOMALY_DETECTED",
                "device": device_ip,
                "timestamp": time.time(),
                "severity": severity,
                "details": {
                    "scores": scores,
                    "context": context or {}
                },
                "status": "NEW"
            }
            return event
        
        return None

if __name__ == "__main__":
    builder = EventBuilder(threshold=2.0) # threshold depends on the ensemble output scale
    result = builder.build_event(
        "192.168.1.105", 
        {"aggregate": 2.5, "isolation_forest": 0.8},
        context={"top_port": 445}
    )
    print(result)
