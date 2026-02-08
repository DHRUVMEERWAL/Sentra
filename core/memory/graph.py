from neo4j import GraphDatabase
from loguru import logger
import os
from datetime import datetime
from typing import Dict, Any, List

class GraphMemory:
    def __init__(self, uri=None, user=None, password=None):
        self.uri = uri or os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.user = user or os.getenv("NEO4J_USER", "neo4j")
        self.password = password or os.getenv("NEO4J_PASSWORD", "password")
        self._driver = None
        
    @property
    def driver(self):
        if self._driver is None:
            try:
                self._driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
                # Test connection
                with self._driver.session() as session:
                    session.run("RETURN 1")
                logger.info("Connected to Neo4j")
            except Exception as e:
                logger.warning(f"Neo4j connection failed: {e}. Using mock mode.")
                self._driver = None
        return self._driver

    def close(self):
        if self._driver:
            self._driver.close()

    def add_device(self, ip: str, mac: str = None, hostname: str = None):
        """Add or update a device node."""
        if not self.driver:
            return
        with self.driver.session() as session:
            session.run("""
                MERGE (d:Device {ip: $ip})
                SET d.mac = $mac, d.hostname = $hostname, d.last_seen = timestamp()
            """, ip=ip, mac=mac, hostname=hostname)

    def add_interaction(self, src_ip: str, dst_ip: str, port: int, proto: str):
        """Record a network interaction."""
        if not self.driver:
            return
        with self.driver.session() as session:
            session.run("""
                MATCH (a:Device {ip: $src_ip})
                MATCH (b:Device {ip: $dst_ip})
                MERGE (a)-[r:TALKED_TO {port: $port, proto: $proto}]->(b)
                SET r.count = coalesce(r.count, 0) + 1, r.last_seen = timestamp()
            """, src_ip=src_ip, dst_ip=dst_ip, port=port, proto=proto)
    
    def add_incident(self, device_ip: str, severity: int, event_type: str, action_taken: str):
        """Store a security incident."""
        if not self.driver:
            logger.debug(f"[MOCK] Incident: {device_ip} - {event_type} (sev: {severity})")
            return
        with self.driver.session() as session:
            session.run("""
                MATCH (d:Device {ip: $ip})
                CREATE (i:Incident {
                    timestamp: timestamp(),
                    severity: $severity,
                    event_type: $event_type,
                    action_taken: $action_taken
                })
                CREATE (d)-[:HAD_INCIDENT]->(i)
            """, ip=device_ip, severity=severity, event_type=event_type, action_taken=action_taken)
    
    def add_threat(self, attacker_ip: str, target_ip: str, attack_type: str):
        """Track a threat/attack relationship."""
        if not self.driver:
            logger.debug(f"[MOCK] Threat: {attacker_ip} -> {target_ip} ({attack_type})")
            return
        with self.driver.session() as session:
            session.run("""
                MERGE (a:Attacker {ip: $attacker_ip})
                MERGE (t:Device {ip: $target_ip})
                MERGE (a)-[r:ATTACKED {type: $attack_type}]->(t)
                SET r.count = coalesce(r.count, 0) + 1, r.last_seen = timestamp()
            """, attacker_ip=attacker_ip, target_ip=target_ip, attack_type=attack_type)
    
    def get_device_context(self, ip: str) -> Dict[str, Any]:
        """Get connected devices, incidents, and relationships."""
        if not self.driver:
            return {"status": "mock", "device": ip, "incidents": [], "connections": []}
        
        with self.driver.session() as session:
            # Get device info and connections
            result = session.run("""
                MATCH (d:Device {ip: $ip})
                OPTIONAL MATCH (d)-[r]-(neighbor)
                OPTIONAL MATCH (d)-[:HAD_INCIDENT]->(i:Incident)
                RETURN d, collect(DISTINCT {rel: type(r), neighbor: neighbor.ip}) as connections,
                       collect(DISTINCT {severity: i.severity, type: i.event_type}) as incidents
            """, ip=ip)
            
            record = result.single()
            if record:
                return {
                    "device": dict(record["d"]) if record["d"] else {},
                    "connections": record["connections"],
                    "incidents": record["incidents"]
                }
            return {"status": "not_found", "device": ip}
    
    def get_attack_history(self, target_ip: str) -> List[Dict[str, Any]]:
        """Get history of attacks against a device."""
        if not self.driver:
            return []
        
        with self.driver.session() as session:
            result = session.run("""
                MATCH (a:Attacker)-[r:ATTACKED]->(t:Device {ip: $ip})
                RETURN a.ip as attacker, r.type as attack_type, r.count as count
                ORDER BY r.count DESC
            """, ip=target_ip)
            return [dict(record) for record in result]

if __name__ == "__main__":
    # Mock usage usually requires running DB
    gm = GraphMemory()
    print(gm.get_device_context("192.168.1.100"))
