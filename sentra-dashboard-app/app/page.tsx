'use client'

import { Sidebar } from '@/components/Sidebar'
import { PageHeader } from '@/components/PageHeader'
import { LiveLogs } from '@/components/LiveLogs'
import { OODACycle } from '@/components/OODACycle'
import { NetworkTopology } from '@/components/NetworkTopology'
import { useAgentState } from '@/hooks/useAgentState'
import { LineChart, Line, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { AlertTriangle, Shield, Zap, TrendingUp, Activity } from 'lucide-react'
import { useState, useEffect } from 'react'

export default function Dashboard() {
  const { agentState, logs, threats, activeThreat, metrics } = useAgentState()
  const [chartData, setChartData] = useState([
    { time: '00:00', threats: 2, blocked: 2, anomalies: 10 },
    { time: '04:00', threats: 5, blocked: 5, anomalies: 25 },
    { time: '08:00', threats: 8, blocked: 7, anomalies: 45 },
    { time: '12:00', threats: 12, blocked: 11, anomalies: 65 },
    { time: '16:00', threats: 18, blocked: 16, anomalies: 95 },
    { time: '20:00', threats: 24, blocked: 22, anomalies: 128 },
  ])

  const threatData = chartData.map(item => ({ time: item.time, threats: item.threats }))
  const networkData = chartData.map(item => ({ time: item.time, anomaly: item.anomalies }))

  // Update chart data in real time
  useEffect(() => {
    if (activeThreat && agentState === 'DEPLOY') {
      setChartData((prev) => {
        const last = prev[prev.length - 1]
        const newPoint = {
          time: new Date().toLocaleTimeString().slice(0, 5),
          threats: last.threats + 1,
          blocked: last.blocked + 1,
          anomalies: last.anomalies + Math.floor(Math.random() * 20) + 10,
        }
        return [...prev.slice(1), newPoint]
      })
    }
  }, [activeThreat, agentState])

  return (
    <div className="flex min-h-screen bg-background">
      <Sidebar />
      <div className="flex-1 ml-64">
        <PageHeader
          title="SENTRA"
          description="Live agent OODA cycle with autonomous threat response"
        />

        <main className="p-8 space-y-8">
          {/* Live KPI Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="p-6 border border-[#262626] rounded-lg bg-[#141414]">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground mb-1">Threats Detected</p>
                  <p className="text-3xl font-bold text-foreground">{metrics.totalThreats}</p>
                  <p className="text-xs text-destructive mt-2">Live: {activeThreat ? '1 Active' : 'None'}</p>
                </div>
                <AlertTriangle className={`w-8 h-8 ${activeThreat ? 'text-destructive animate-pulse' : 'text-muted-foreground'} opacity-80`} />
              </div>
            </div>

            <div className="p-6 border border-[#262626] rounded-lg bg-[#141414]">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground mb-1">Blocked</p>
                  <p className="text-3xl font-bold text-green-500">{metrics.blocked}</p>
                  <p className="text-xs text-green-500 mt-2">{((metrics.blocked / metrics.totalThreats) * 100).toFixed(1)}% success</p>
                </div>
                <Shield className="w-8 h-8 text-green-500 opacity-80" />
              </div>
            </div>

            <div className="p-6 border border-[#262626] rounded-lg bg-[#141414]">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground mb-1">Anomalies</p>
                  <p className="text-3xl font-bold text-foreground">{metrics.anomalies}</p>
                  <p className="text-xs text-secondary mt-2">This session</p>
                </div>
                <Zap className="w-8 h-8 text-secondary opacity-80" />
              </div>
            </div>

            <div className="p-6 border border-[#262626] rounded-lg bg-[#141414]">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground mb-1">Agent State</p>
                  <p className={`text-3xl font-bold font-mono ${agentState === 'DEPLOY' ? 'text-destructive' : agentState === 'DECIDE' ? 'text-warning' : 'text-primary'}`}>{agentState}</p>
                  <p className="text-xs text-green-500 mt-2 flex items-center gap-1"><Activity className="w-3 h-3" /> Active</p>
                </div>
                <div className={`w-3 h-3 rounded-full ${agentState === 'DEPLOY' ? 'bg-destructive animate-pulse' : agentState === 'DECIDE' ? 'bg-warning' : 'bg-primary'}`} />
              </div>
            </div>
          </div>

          {/* OODA Cycle and Live Logs */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-1">
              <OODACycle state={agentState} threat={activeThreat ? { ip: activeThreat.ip, severity: activeThreat.severity } : null} />
            </div>
            <div className="lg:col-span-2">
              <div className="p-6 border border-[#262626] rounded-lg bg-[#141414]">
                <h3 className="text-lg font-semibold text-foreground mb-4">Agent Console</h3>
                <LiveLogs logs={logs} />
              </div>
            </div>
          </div>

          {/* Network Topology */}
          <NetworkTopology />

          {/* Charts - Real-time updating */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="p-6 border border-[#262626] rounded-lg bg-[#141414]">
              <h3 className="text-lg font-semibold text-foreground mb-4">Threat Response Timeline</h3>
              <ResponsiveContainer width="100%" height={300}>
                <AreaChart data={chartData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                  <defs>
                    <linearGradient id="colorThreat" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#06b6d4" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#262626" />
                  <XAxis dataKey="time" stroke="#a3a3a3" />
                  <YAxis stroke="#a3a3a3" />
                  <Tooltip contentStyle={{ backgroundColor: '#1a1a1a', border: '1px solid #262626' }} />
                  <Area type="monotone" dataKey="threats" stroke="#06b6d4" fill="url(#colorThreat)" name="Detected" />
                </AreaChart>
              </ResponsiveContainer>
            </div>

            <div className="p-6 border border-[#262626] rounded-lg bg-[#141414]">
              <h3 className="text-lg font-semibold text-foreground mb-4">Anomaly Density</h3>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={chartData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#262626" />
                  <XAxis dataKey="time" stroke="#a3a3a3" />
                  <YAxis stroke="#a3a3a3" />
                  <Tooltip contentStyle={{ backgroundColor: '#1a1a1a', border: '1px solid #262626' }} />
                  <Line type="monotone" dataKey="anomalies" stroke="#ef4444" strokeWidth={2} dot={false} name="Anomalies" />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Live Threat Queue */}
          <div className="p-6 border border-[#262626] rounded-lg bg-[#141414]">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-foreground">Live Threat Queue</h3>
              <div className="text-xs text-muted-foreground">{threats.length} threats tracked</div>
            </div>
            <div className="space-y-3">
              {threats.length === 0 ? (
                <p className="text-sm text-muted-foreground text-center py-8">Waiting for threat activity...</p>
              ) : (
                threats.map((threat, i) => (
                  <div key={threat.id} className="flex items-start gap-4 pb-3 border-b border-[#262626] last:border-0">
                    <div className={`w-2 h-2 rounded-full mt-2 flex-shrink-0 ${threat.status === 'HONEYPOTTED' ? 'bg-green-500' :
                      threat.status === 'BLOCKED' ? 'bg-green-500' :
                        threat.status === 'ANALYZING' ? 'bg-warning' : 'bg-destructive animate-pulse'
                      }`} />
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <p className="text-sm text-foreground font-mono">{threat.ip}</p>
                        <span className={`text-xs px-2 py-0.5 rounded ${threat.status === 'HONEYPOTTED' ? 'bg-green-500/20 text-green-400' :
                          threat.status === 'BLOCKED' ? 'bg-green-500/20 text-green-400' :
                            threat.status === 'ANALYZING' ? 'bg-yellow-500/20 text-yellow-400' :
                              'bg-red-500/20 text-red-400'
                          }`}>
                          {threat.status}
                        </span>
                      </div>
                      <p className="text-xs text-muted-foreground mt-1">Severity: {threat.severity}/100 • Score: {threat.anomalyScore.toLocaleString()}</p>
                      <p className="text-xs text-muted-foreground">{new Date(threat.timestamp).toLocaleTimeString()}</p>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </main>
      </div>
    </div>
  )
}
