"""
Dashboard Event Publisher

Publishes events from Sentra Core to the Dashboard API.
"""

import os
import json
import requests
from datetime import datetime
from loguru import logger
from typing import Dict, Any, Optional

# Dashboard API URL
DASHBOARD_API_URL = os.getenv("DASHBOARD_API_URL", "http://localhost:8080")


class DashboardPublisher:
    """Publishes events to the dashboard API."""
    
    def __init__(self, api_url: str = None):
        self.api_url = api_url or DASHBOARD_API_URL
        self._enabled = True
        
    def publish(self, event_type: str, data: Dict[str, Any] = None) -> bool:
        """
        Publish an event to the dashboard.
        
        Args:
            event_type: Type of event (ATTACK_DETECTED, HONEYPOT_REDIRECT, etc.)
            data: Additional event data
            
        Returns:
            True if successfully published
        """
        if not self._enabled:
            return False
            
        event = {
            "type": event_type,
            "timestamp": datetime.now().isoformat(),
            **(data or {})
        }
        
        try:
            response = requests.post(
                f"{self.api_url}/api/events",
                json=event,
                timeout=2
            )
            return response.status_code == 200
        except Exception as e:
            logger.debug(f"Dashboard publish failed (dashboard may not be running): {e}")
            return False
    
    def attack_detected(self, device: str, severity: int, score: float):
        """Publish attack detection event."""
        return self.publish("ATTACK_DETECTED", {
            "device": device,
            "severity": severity,
            "score": score,
            "message": f"Attack detected on {device} with severity {severity}"
        })
    
    def honeypot_redirect(self, attacker_ip: str, target_ip: str):
        """Publish honeypot redirect event."""
        return self.publish("HONEYPOT_REDIRECT", {
            "attacker": attacker_ip,
            "target": target_ip,
            "message": f"Attacker {attacker_ip} redirected to honeypot"
        })
    
    def llm_decision(self, intent: str, target: str, reason: str):
        """Publish LLM decision event."""
        return self.publish("LLM_DECISION", {
            "intent": intent,
            "target": target,
            "reason": reason,
            "message": f"LLM decided: {intent} for {target}"
        })
    
    def agent_state(self, state: str, details: Dict[str, Any] = None):
        """Publish agent state change."""
        return self.publish("AGENT_STATE", {
            "state": state,
            "details": details or {},
            "message": f"Agent state: {state}"
        })
    
    def deception_success(self, attacker_ip: str, fake_data_size: int):
        """Publish deception success event."""
        return self.publish("DECEPTION", {
            "attacker": attacker_ip,
            "fake_data_bytes": fake_data_size,
            "message": f"Sent {fake_data_size} bytes of fake data to {attacker_ip}"
        })


# Global instance
dashboard = DashboardPublisher()


if __name__ == "__main__":
    # Test publishing
    pub = DashboardPublisher()
    
    print("Testing dashboard publisher...")
    
    result = pub.attack_detected("192.168.1.100", 85, 124587.6)
    print(f"Attack detected: {result}")
    
    result = pub.honeypot_redirect("10.0.0.5", "192.168.1.100")
    print(f"Honeypot redirect: {result}")
    
    result = pub.llm_decision("DEPLOY_HONEYPOT", "192.168.1.100", "High severity anomaly")
    print(f"LLM decision: {result}")
