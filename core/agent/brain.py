from typing import TypedDict, Annotated, List, Dict, Any
import operator
from langgraph.graph import StateGraph, END
from loguru import logger
import json

# Import memory and LLM
from core.agent.llm import OllamaClient, get_ollama_client
from core.memory.graph import GraphMemory
from core.memory.vector import VectorMemory

# State Definition
class AgentState(TypedDict):
    event: Dict[str, Any]
    context: Dict[str, Any]
    analysis: str
    intent: Dict[str, Any]
    status: str

class SentraAgent:
    """
    Agentic cybersecurity system using LangGraph, Ollama LLM, and memory.
    """
    
    def __init__(
        self, 
        llm_client: OllamaClient = None, 
        graph_mem: GraphMemory = None, 
        vector_mem: VectorMemory = None
    ):
        # Initialize components with defaults
        self.llm = llm_client or get_ollama_client()
        self.graph_mem = graph_mem or GraphMemory()
        self.vector_mem = vector_mem or VectorMemory()
        self.workflow = self._build_graph()
        
        logger.info(f"SentraAgent initialized | LLM: {self.llm.model} | Available: {self.llm.is_available()}")

    def _build_graph(self):
        builder = StateGraph(AgentState)

        builder.add_node("analyze", self.analyze_node)
        builder.add_node("decide", self.decide_node)
        builder.add_node("deploy", self.deploy_node)
        builder.add_node("monitor", self.monitor_node)

        builder.set_entry_point("analyze")

        builder.add_edge("analyze", "decide")
        
        # Conditional edge: If intent is harmful/active -> deploy, else monitor
        builder.add_conditional_edges(
            "decide",
            self._decide_next_step,
            {
                "deploy": "deploy",
                "monitor": "monitor",
                "ignore": END
            }
        )
        
        builder.add_edge("deploy", "monitor")
        builder.add_edge("monitor", END)

        return builder.compile()

    # --- Nodes ---

    def analyze_node(self, state: AgentState):
        logger.info("Agent State: ANALYZE")
        event = state['event']
        device_ip = event.get('device')
        
        # 1. Gather Context from Memory
        context = {}
        
        # Graph memory - device relationships and past incidents
        graph_context = self.graph_mem.get_device_context(device_ip)
        context['graph_data'] = graph_context
        
        # Vector memory - similar past incidents
        vector_context = self.vector_mem.get_context_for_analysis(
            device_ip, 
            event.get('event_type', 'ANOMALY')
        )
        context['history'] = vector_context
        
        # 2. LLM Analysis
        if self.llm.is_available():
            analysis = self.llm.analyze_security_event(event, context)
        else:
            # Fallback heuristic analysis
            sev = event.get('severity', 0)
            analysis = f"Automated analysis: Device {device_ip} is exhibiting anomalous behavior (Severity: {sev}). "
            if sev > 80:
                analysis += "High threat level - immediate action recommended."
            elif sev > 50:
                analysis += "Moderate threat level - close monitoring advised."
            else:
                analysis += "Low threat level - routine monitoring."

        return {"context": context, "analysis": analysis, "status": "ANALYZED"}

    def decide_node(self, state: AgentState):
        logger.info("Agent State: DECIDE")
        analysis = state['analysis']
        event = state['event']
        
        # LLM Decision
        if self.llm.is_available():
            intent = self.llm.decide_action(analysis, event)
        else:
            # Simple heuristic fallback
            sev = event.get('severity', 0)
            if sev > 70:
                intent = {
                    "intent": "DEPLOY_HONEYPOT", 
                    "target": event['device'],
                    "reason": "High severity anomaly detected",
                    "confidence": 0.8
                }
            elif sev > 40:
                intent = {
                    "intent": "MONITOR_CLOSELY",
                    "reason": "Moderate anomaly - increased surveillance",
                    "confidence": 0.6
                }
            else:
                intent = {
                    "intent": "IGNORE",
                    "reason": "Low severity - normal variance",
                    "confidence": 0.5
                }

        return {"intent": intent, "status": "DECIDED"}

    def deploy_node(self, state: AgentState):
        intent = state['intent']
        event = state['event']
        logger.info(f"Agent State: DEPLOY | Intent: {intent}")
        
        # Store incident in memory
        try:
            # Graph memory - store incident
            self.graph_mem.add_incident(
                device_ip=event.get('device'),
                severity=event.get('severity', 0),
                event_type=event.get('event_type', 'ANOMALY'),
                action_taken=intent.get('intent', 'UNKNOWN')
            )
            
            # Vector memory - store for future similarity search
            self.vector_mem.add_incident_memory(
                device_ip=event.get('device'),
                severity=event.get('severity', 0),
                event_type=event.get('event_type', 'ANOMALY'),
                analysis=state.get('analysis', ''),
                action_taken=intent.get('intent', 'UNKNOWN')
            )
        except Exception as e:
            logger.warning(f"Memory storage failed: {e}")
        
        return {"status": "DEPLOYED"}

    def monitor_node(self, state: AgentState):
        logger.info("Agent State: MONITOR")
        return {"status": "MONITORING"}

    def _decide_next_step(self, state: AgentState):
        intent_type = state['intent'].get('intent', '').upper()
        if "DEPLOY" in intent_type or "BLOCK" in intent_type:
            return "deploy"
        elif "MONITOR" in intent_type:
            return "monitor"
        else:
            return "ignore"

    def run(self, event: Dict[str, Any]):
        """Run the agent for a given event."""
        initial_state = AgentState(
            event=event, 
            context={}, 
            analysis="", 
            intent={}, 
            status="NEW"
        )
        return self.workflow.invoke(initial_state)


if __name__ == "__main__":
    # Test the agent
    agent = SentraAgent()
    
    # Test event
    evt = {
        "device": "192.168.1.100", 
        "severity": 85, 
        "event_type": "ANOMALY"
    }
    
    print("Testing SentraAgent with event:")
    print(json.dumps(evt, indent=2))
    print("\n" + "=" * 50 + "\n")
    
    result = agent.run(evt)
    print("\nResult:")
    print(json.dumps(result, indent=2, default=str))
