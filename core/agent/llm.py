"""
Ollama LLM Client for Sentra

Provides local inference using Ollama with Gemma3:1b model.
"""

import os
import json
import requests
from typing import Dict, Any, Optional, List
from loguru import logger


class OllamaClient:
    """
    Client for Ollama local LLM inference.
    Uses Gemma3:270m by default for fast, lightweight CPU inference.
    """
    
    def __init__(
        self, 
        host: str = None,
        model: str = "gemma3:270m",
        timeout: int = 60
    ):
        self.host = host or os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self.model = model
        self.timeout = timeout
        self._available = None
        
    def is_available(self) -> bool:
        """Check if Ollama server is running and model is available."""
        if self._available is not None:
            return self._available
            
        try:
            response = requests.get(f"{self.host}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                model_names = [m.get("name", "") for m in models]
                self._available = any(self.model in name for name in model_names)
                if not self._available:
                    logger.warning(f"Model {self.model} not found. Available: {model_names}")
            else:
                self._available = False
        except Exception as e:
            logger.warning(f"Ollama not available: {e}")
            self._available = False
            
        return self._available
    
    def generate(
        self, 
        prompt: str,
        system_prompt: str = None,
        temperature: float = 0.7,
        max_tokens: int = 512
    ) -> str:
        """
        Generate a response from the LLM.
        
        Args:
            prompt: The user prompt
            system_prompt: Optional system context
            temperature: Creativity (0-1)
            max_tokens: Max response length
            
        Returns:
            Generated text response
        """
        if not self.is_available():
            logger.warning("Ollama not available, returning fallback response")
            return self._fallback_response(prompt)
        
        # Build messages for chat format
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }
        
        try:
            response = requests.post(
                f"{self.host}/api/chat",
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("message", {}).get("content", "")
            else:
                logger.error(f"Ollama error: {response.status_code} - {response.text}")
                return self._fallback_response(prompt)
                
        except Exception as e:
            logger.error(f"Ollama request failed: {e}")
            return self._fallback_response(prompt)
    
    def _fallback_response(self, prompt: str) -> str:
        """Provide a heuristic-based fallback when LLM is unavailable."""
        prompt_lower = prompt.lower()
        
        if "attack" in prompt_lower or "threat" in prompt_lower or "anomaly" in prompt_lower:
            return json.dumps({
                "intent": "DEPLOY_HONEYPOT",
                "reason": "High threat level detected - deploying deception",
                "confidence": 0.85
            })
        elif "analyze" in prompt_lower:
            return "Automated analysis: Potential security incident detected. Recommend monitoring and honeypot deployment for threat intelligence gathering."
        else:
            return json.dumps({
                "intent": "MONITOR_CLOSELY",
                "reason": "Insufficient threat indicators for active response",
                "confidence": 0.6
            })
    
    def analyze_security_event(self, event: Dict[str, Any], context: Dict[str, Any] = None) -> str:
        """
        Specialized method for security event analysis.
        
        Args:
            event: Security event data (device, severity, type)
            context: Additional context (history, graph data)
            
        Returns:
            Analysis text
        """
        system_prompt = """You are Sentra, an AI cybersecurity analyst for IoT networks.
Your role is to analyze security events and provide actionable recommendations.
Always prioritize:
1. Threat assessment and severity
2. Potential attack vectors
3. Recommended defensive actions (honeypot deployment, monitoring, blocking)
Keep responses concise and security-focused."""

        context_str = json.dumps(context) if context else "No additional context"
        
        prompt = f"""Analyze this security event:
Device: {event.get('device', 'Unknown')}
Severity: {event.get('severity', 'Unknown')}
Event Type: {event.get('event_type', 'ANOMALY')}

Historical Context: {context_str}

Provide a brief threat assessment and recommended action."""

        return self.generate(prompt, system_prompt=system_prompt)
    
    def decide_action(self, analysis: str, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Decide on defensive action based on analysis.
        
        Args:
            analysis: The security analysis text
            event: Original event data
            
        Returns:
            JSON with intent and parameters
        """
        system_prompt = """You are a security decision engine. Based on the analysis, output a JSON object with:
- "intent": One of ["DEPLOY_HONEYPOT", "MONITOR_CLOSELY", "BLOCK_IP", "IGNORE"]
- "target": The IP address to act on
- "reason": Brief justification
- "confidence": 0.0-1.0

Output ONLY valid JSON, no markdown or explanation."""

        prompt = f"""Analysis: {analysis}
Event Device: {event.get('device')}
Event Severity: {event.get('severity')}

Decide the appropriate defensive action. Output JSON only."""

        response = self.generate(prompt, system_prompt=system_prompt, temperature=0.3)
        
        # Try to parse JSON from response
        try:
            # Clean up common LLM issues
            clean = response.strip()
            if clean.startswith("```"):
                clean = clean.split("```")[1]
                if clean.startswith("json"):
                    clean = clean[4:]
            return json.loads(clean)
        except:
            # Return structured fallback
            return {
                "intent": "DEPLOY_HONEYPOT" if event.get('severity', 0) > 70 else "MONITOR_CLOSELY",
                "target": event.get('device'),
                "reason": "Fallback decision due to parse error",
                "confidence": 0.5
            }


# Singleton instance for easy import
_client = None

def get_ollama_client(model: str = "gemma3:270m") -> OllamaClient:
    """Get or create the Ollama client singleton."""
    global _client
    if _client is None:
        _client = OllamaClient(model=model)
    return _client


if __name__ == "__main__":
    # Test the client
    client = OllamaClient()
    
    print(f"Ollama Available: {client.is_available()}")
    
    if client.is_available():
        # Test security analysis
        event = {"device": "192.168.1.100", "severity": 85, "event_type": "ANOMALY"}
        analysis = client.analyze_security_event(event)
        print(f"\nAnalysis:\n{analysis}")
        
        # Test decision
        decision = client.decide_action(analysis, event)
        print(f"\nDecision:\n{json.dumps(decision, indent=2)}")
    else:
        print("\nOllama not running. Start with: ollama serve")
        print("Then pull model: ollama pull gemma3:1b")
