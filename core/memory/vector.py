import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any
from loguru import logger
from datetime import datetime
import uuid
import os
import json

class VectorMemory:
    """
    Vector memory using ChromaDB for semantic search of past incidents.
    """
    
    def __init__(self, host=None, port=None):
        self.host = host or os.getenv("CHROMA_HOST", "localhost")
        self.port = port or int(os.getenv("CHROMA_PORT", "8000"))
        self._client = None
        self._collection = None
        
    @property
    def collection(self):
        if self._collection is None:
            try:
                self._client = chromadb.HttpClient(host=self.host, port=self.port)
                self._collection = self._client.get_or_create_collection(
                    name="sentra_memories",
                    metadata={"description": "Security incident memories"}
                )
                logger.info(f"Connected to ChromaDB at {self.host}:{self.port}")
            except Exception as e:
                logger.warning(f"ChromaDB connection failed: {e}. Using in-memory fallback.")
                self._client = chromadb.Client()
                self._collection = self._client.get_or_create_collection(name="sentra_memories")
        return self._collection

    def add_memory(self, text: str, metadata: Dict[str, Any] = None):
        """Add a text memory (e.g. incident summary)."""
        self.collection.add(
            documents=[text],
            metadatas=[metadata or {}],
            ids=[str(uuid.uuid4())]
        )

    def add_incident_memory(
        self, 
        device_ip: str, 
        severity: int, 
        event_type: str,
        analysis: str,
        action_taken: str
    ):
        """
        Store a security incident as searchable memory.
        
        Args:
            device_ip: Target device IP
            severity: Threat severity (0-100)
            event_type: Type of event (ANOMALY, ATTACK, etc.)
            analysis: LLM or automated analysis text
            action_taken: What defensive action was deployed
        """
        text = f"""Security Incident - Device: {device_ip}
Severity: {severity}
Type: {event_type}
Analysis: {analysis}
Action: {action_taken}"""
        
        metadata = {
            "device_ip": device_ip,
            "severity": severity,
            "event_type": event_type,
            "action_taken": action_taken,
            "timestamp": datetime.now().isoformat()
        }
        
        self.add_memory(text, metadata)
        logger.debug(f"Stored incident memory for {device_ip}")

    def query_similar(self, text: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Find similar past memories."""
        try:
            results = self.collection.query(
                query_texts=[text],
                n_results=n_results
            )
            # results structure is a bit nested
            documents = results.get('documents', [[]])[0]
            metadatas = results.get('metadatas', [[]])[0]
            distances = results.get('distances', [[]])[0]
            
            output = []
            for doc, meta, dist in zip(documents, metadatas, distances):
                output.append({
                    "content": doc,
                    "metadata": meta,
                    "distance": dist,
                    "relevance": 1.0 - min(dist, 1.0)  # Convert distance to relevance
                })
            return output
        except Exception as e:
            logger.warning(f"Vector query failed: {e}")
            return []
    
    def get_device_history(self, device_ip: str, n_results: int = 10) -> List[Dict[str, Any]]:
        """Get past incidents for a specific device."""
        return self.query_similar(f"Device {device_ip} security incident", n_results)
    
    def get_attack_patterns(self, attack_type: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Find similar past attacks of a given type."""
        return self.query_similar(f"{attack_type} attack pattern behavior", n_results)
    
    def get_context_for_analysis(self, device_ip: str, event_type: str) -> str:
        """
        Build a context string for LLM analysis based on past incidents.
        
        Args:
            device_ip: Device being analyzed
            event_type: Current event type
            
        Returns:
            Context string for LLM prompt
        """
        # Get device history
        history = self.get_device_history(device_ip, n_results=3)
        
        if not history:
            return "No prior incidents recorded for this device."
        
        context_parts = ["Previous incidents for this device:"]
        for i, mem in enumerate(history, 1):
            meta = mem.get("metadata", {})
            context_parts.append(f"{i}. {meta.get('event_type', 'Unknown')} (Severity: {meta.get('severity', 'N/A')}) - Action: {meta.get('action_taken', 'None')}")
        
        return "\n".join(context_parts)

if __name__ == "__main__":
    vm = VectorMemory()
    
    # Test adding an incident
    vm.add_incident_memory(
        device_ip="192.168.1.100",
        severity=85,
        event_type="ANOMALY",
        analysis="High traffic volume detected, potential SYN flood",
        action_taken="DEPLOY_HONEYPOT"
    )
    
    # Test querying
    similar = vm.query_similar("camera attack")
    print("Similar incidents:", json.dumps(similar, indent=2))
