"""
Neo4j Schema Initialization

Creates the necessary constraints, indexes, and initial nodes
for the Sentra memory graph.
"""

from neo4j import GraphDatabase
from loguru import logger
import os
import sys

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def init_schema():
    """Initialize Neo4j schema with constraints and indexes."""
    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "password")
    
    logger.info(f"Connecting to Neo4j at {uri}...")
    
    try:
        driver = GraphDatabase.driver(uri, auth=(user, password))
        
        with driver.session() as session:
            # 1. Create constraints for unique IPs
            logger.info("Creating constraints...")
            
            # Device constraint
            try:
                session.run("""
                    CREATE CONSTRAINT device_ip IF NOT EXISTS
                    FOR (d:Device) REQUIRE d.ip IS UNIQUE
                """)
                logger.success("Created Device IP constraint")
            except Exception as e:
                logger.debug(f"Device constraint: {e}")
            
            # Attacker constraint
            try:
                session.run("""
                    CREATE CONSTRAINT attacker_ip IF NOT EXISTS
                    FOR (a:Attacker) REQUIRE a.ip IS UNIQUE
                """)
                logger.success("Created Attacker IP constraint")
            except Exception as e:
                logger.debug(f"Attacker constraint: {e}")
            
            # 2. Create indexes for faster lookups
            logger.info("Creating indexes...")
            
            try:
                session.run("""
                    CREATE INDEX incident_timestamp IF NOT EXISTS
                    FOR (i:Incident) ON (i.timestamp)
                """)
                logger.success("Created Incident timestamp index")
            except Exception as e:
                logger.debug(f"Incident index: {e}")
            
            try:
                session.run("""
                    CREATE INDEX incident_severity IF NOT EXISTS
                    FOR (i:Incident) ON (i.severity)
                """)
                logger.success("Created Incident severity index")
            except Exception as e:
                logger.debug(f"Severity index: {e}")
            
            # 3. Create sample nodes to establish schema
            logger.info("Creating initial schema nodes...")
            
            session.run("""
                MERGE (d:Device {ip: '0.0.0.0'})
                SET d.hostname = 'schema_placeholder',
                    d.mac = '00:00:00:00:00:00',
                    d.last_seen = timestamp(),
                    d.is_placeholder = true
            """)
            
            session.run("""
                MERGE (a:Attacker {ip: '0.0.0.0'})
                SET a.first_seen = timestamp(),
                    a.attack_count = 0,
                    a.is_placeholder = true
            """)
            
            session.run("""
                MATCH (d:Device {ip: '0.0.0.0'})
                MERGE (d)-[:HAD_INCIDENT]->(i:Incident {
                    timestamp: timestamp(),
                    severity: 0,
                    event_type: 'SCHEMA_INIT',
                    action_taken: 'NONE',
                    is_placeholder: true
                })
            """)
            
            logger.success("Schema nodes created")
            
            # 4. Verify schema
            logger.info("Verifying schema...")
            result = session.run("""
                CALL db.schema.visualization()
            """)
            
            # Show node labels
            labels_result = session.run("CALL db.labels()")
            labels = [r['label'] for r in labels_result]
            logger.info(f"Node labels: {labels}")
            
            # Show relationship types
            rels_result = session.run("CALL db.relationshipTypes()")
            rels = [r['relationshipType'] for r in rels_result]
            logger.info(f"Relationship types: {rels}")
            
            # Show property keys
            props_result = session.run("CALL db.propertyKeys()")
            props = [r['propertyKey'] for r in props_result]
            logger.info(f"Property keys: {props}")
            
        driver.close()
        logger.success("Neo4j schema initialization complete!")
        return True
        
    except Exception as e:
        logger.error(f"Failed to initialize Neo4j schema: {e}")
        return False


if __name__ == "__main__":
    init_schema()
