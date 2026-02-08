from typing import Dict, Any, Tuple
from loguru import logger

class PolicyEngine:
    def __init__(self):
        self.forbidden_targets = ["192.168.1.1", "127.0.0.1"] # Gateway, Localhost
        self.allowed_actions = ["DEPLOY_HONEYPOT", "MONITOR_CLOSELY", "BLOCK_IP"]

    def validate_action(self, intent: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Check if the intended action is safe and allowed.
        """
        action = intent.get("intent")
        target = intent.get("target")

        if action not in self.allowed_actions:
            return False, f"Action {action} is not in allowed list."

        if target in self.forbidden_targets:
            return False, f"Target {target} is a protected critical infrastructure."

        # Safety check: Do not block subnets, only single IPs (heuristic)
        if action == "BLOCK_IP" and "/" in target and not target.endswith("/32"):
             return False, "Broad subnet blocking is forbidden."

        return True, "Action permitted."

class DeceptionManager:
    """
    Manages HoneyPot lifecycle.
    """
    def __init__(self):
        pass

    def deploy_honeypot(self, device_ip: str, port: int) -> bool:
        """
        Spin up a honeypot mimic for the device.
        In a real scenario, this calls Docker API.
        """
        logger.info(f"DEPLOYING HONEYPOT for {device_ip} on port {port}")
        # Docker logic here:
        # client.containers.run("cowrie/cowrie", ports={f"{port}/tcp": 2222}, detach=True)
        return True

if __name__ == "__main__":
    pe = PolicyEngine()
    dm = DeceptionManager()
    
    intent = {"intent": "DEPLOY_HONEYPOT", "target": "10.0.0.50"}
    allowed, msg = pe.validate_action(intent)
    if allowed:
        print(msg)
        dm.deploy_honeypot(intent['target'], 80)
    else:
        print(f"BLOCKED: {msg}")
