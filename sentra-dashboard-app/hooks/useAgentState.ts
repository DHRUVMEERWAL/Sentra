'use client'

import { useState, useEffect } from 'react'

export type AgentState = 'MONITOR' | 'ANALYZE' | 'DECIDE' | 'DEPLOY' | 'IDLE'

export interface AgentLog {
  timestamp: number
  level: 'INFO' | 'DEBUG' | 'WARNING' | 'CRITICAL' | 'SUCCESS'
  message: string
  component: string
}

export interface ThreatEvent {
  id: string
  ip: string
  timestamp: number
  severity: number
  anomalyScore: number
  status: 'DETECTED' | 'ANALYZING' | 'HONEYPOTTED' | 'BLOCKED'
  reason: string
}

const generateAttackerIP = () => {
  const lastOctet = Math.floor(Math.random() * 10) + 1
  return `172.18.0.${lastOctet}`
}

export const useAgentState = () => {
  const [agentState, setAgentState] = useState<AgentState>('MONITOR')
  const [logs, setLogs] = useState<AgentLog[]>([])
  const [threats, setThreats] = useState<ThreatEvent[]>([])
  const [activeThreat, setActiveThreat] = useState<ThreatEvent | null>(null)
  const [metrics, setMetrics] = useState({
    totalThreats: 28,
    blocked: 27,
    anomalies: 142,
    healthScore: 99.8,
  })

  const addLog = (level: AgentLog['level'], message: string, component: string) => {
    setLogs((prev) => [
      ...prev.slice(-49),
      {
        timestamp: Date.now(),
        level,
        message,
        component,
      },
    ])
  }

  const createThreat = (): ThreatEvent => ({
    id: Math.random().toString(36).slice(2),
    ip: generateAttackerIP(),
    timestamp: Date.now(),
    severity: Math.floor(Math.random() * 40) + 60,
    anomalyScore: Math.floor(Math.random() * 1000000),
    status: 'DETECTED',
    reason: '',
  })

  // Simulate OODA cycle
  useEffect(() => {
    const oodaInterval = setInterval(() => {
      const cycle = ['MONITOR', 'ANALYZE', 'DECIDE', 'DEPLOY', 'MONITOR']
      setAgentState((prev) => {
        const currentIndex = cycle.indexOf(prev as string)
        return cycle[(currentIndex + 1) % cycle.length] as AgentState
      })
    }, 8000)

    return () => clearInterval(oodaInterval)
  }, [])

  // Generate threats and process them
  useEffect(() => {
    const threatInterval = setInterval(() => {
      const threat = createThreat()
      setActiveThreat(threat)
      addLog('CRITICAL', `!!! ATTACK DETECTED !!! Severity: ${threat.severity}`, 'core.agent.brain')
      
      setThreats((prev) => [threat, ...prev.slice(0, 9)])
      setMetrics((prev) => ({
        ...prev,
        totalThreats: prev.totalThreats + 1,
        anomalies: prev.anomalies + Math.floor(Math.random() * 10) + 5,
      }))
    }, 12000)

    return () => clearInterval(threatInterval)
  }, [])

  // Simulate agent reasoning based on state
  useEffect(() => {
    if (agentState === 'MONITOR' && activeThreat) {
      addLog('INFO', 'Agent State: MONITOR', 'core.agent.brain')
      addLog('DEBUG', `Processing batch of ${Math.floor(Math.random() * 50) + 30} packets...`, '__main__')
    } else if (agentState === 'ANALYZE' && activeThreat) {
      addLog('INFO', 'Agent State: ANALYZE', 'core.agent.brain')
      addLog('DEBUG', `Z-Score: ${(Math.random() * 2).toFixed(2)} | Base: ${Math.floor(Math.random() * 200000)} ± ${Math.floor(Math.random() * 80000)}`, '__main__')
      addLog('INFO', `[DEFENSE] Anomaly Score: ${activeThreat.anomalyScore.toFixed(4)}`, '__main__')
    } else if (agentState === 'DECIDE' && activeThreat) {
      addLog('INFO', 'Agent State: DECIDE', 'core.agent.brain')
      addLog('CRITICAL', `AGENT RESPONSE: {'intent': 'DEPLOY_HONEYPOT', 'target': '${activeThreat.ip}'}`, '__main__')
    } else if (agentState === 'DEPLOY' && activeThreat) {
      addLog('INFO', 'Agent State: DEPLOY', 'core.agent.brain')
      addLog('INFO', `[DECEPTION] HONEYPOTTED Attacker ${activeThreat.ip} redirected to Cowrie honeypot`, 'core.deception.deception')
      addLog('INFO', `[DECEPTION] FAKE DATA SENT Sent ${Math.floor(Math.random() * 100) + 50} bytes of fake RTSP data to ${activeThreat.ip}`, 'core.deception.deception')
      addLog('SUCCESS', `[DECEPTION] SUCCESS Attacker ${activeThreat.ip} is now receiving fake data!`, 'core.deception.deception')
      
      setThreats((prev) => prev.map((t) => (t.id === activeThreat.id ? { ...t, status: 'HONEYPOTTED' } : t)))
      setMetrics((prev) => ({ ...prev, blocked: prev.blocked + 1 }))
    }
  }, [agentState, activeThreat])

  return { agentState, logs, threats, activeThreat, metrics }
}
