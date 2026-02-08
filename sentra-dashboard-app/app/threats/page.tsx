'use client'

import { Sidebar } from '@/components/Sidebar'
import { PageHeader } from '@/components/PageHeader'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { AlertTriangle, Clock, MapPin, User } from 'lucide-react'

const threats = [
  {
    id: 1,
    severity: 'critical',
    title: 'Honeypot Engagement Detected',
    description: 'Intruder accessing deception environment',
    source: '192.168.1.105',
    user: 'unknown',
    time: '2 minutes ago',
    status: 'active',
  },
  {
    id: 2,
    severity: 'high',
    title: 'Suspicious Login Pattern',
    description: 'Multiple failed login attempts from new location',
    source: '203.45.67.89',
    user: 'john.doe',
    time: '15 minutes ago',
    status: 'blocked',
  },
  {
    id: 3,
    severity: 'high',
    title: 'Unusual File Access',
    description: 'Accessing sensitive files outside normal patterns',
    source: '10.0.0.42',
    user: 'sarah.smith',
    time: '32 minutes ago',
    status: 'contained',
  },
  {
    id: 4,
    severity: 'medium',
    title: 'Data Exfiltration Attempt',
    description: 'Large data transfer detected to external server',
    source: '172.16.0.18',
    user: 'mike.wilson',
    time: '1 hour ago',
    status: 'blocked',
  },
  {
    id: 5,
    severity: 'medium',
    title: 'Privilege Escalation',
    description: 'Attempt to elevate user permissions detected',
    source: '10.0.0.89',
    user: 'admin_user',
    time: '2 hours ago',
    status: 'blocked',
  },
]

const severityColor = {
  critical: 'bg-destructive/20 text-destructive border-destructive/30',
  high: 'bg-warning/20 text-warning border-warning/30',
  medium: 'bg-primary/20 text-primary border-primary/30',
  low: 'bg-secondary/20 text-secondary border-secondary/30',
}

const statusColor = {
  active: 'bg-destructive/10 text-destructive border-destructive/30',
  blocked: 'bg-green-500/10 text-green-400 border-green-500/30',
  contained: 'bg-primary/10 text-primary border-primary/30',
}

export default function ThreatsPage() {
  return (
    <div className="flex min-h-screen bg-background">
      <Sidebar />
      <div className="flex-1 ml-64">
        <PageHeader 
          title="Active Threats" 
          description="Monitor and manage security threats in real-time"
        />
        
        <main className="p-8 space-y-6">
          {/* Stats */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="p-6 border border-[#262626] rounded-lg bg-[#141414]">
              <p className="text-sm text-muted-foreground mb-2">Critical Threats</p>
              <p className="text-4xl font-bold text-destructive">1</p>
              <p className="text-xs text-muted-foreground mt-2">Requires immediate attention</p>
            </div>
            <div className="p-6 border border-[#262626] rounded-lg bg-[#141414]">
              <p className="text-sm text-muted-foreground mb-2">High Priority</p>
              <p className="text-4xl font-bold text-warning">2</p>
              <p className="text-xs text-muted-foreground mt-2">Actively being investigated</p>
            </div>
            <div className="p-6 border border-[#262626] rounded-lg bg-[#141414]">
              <p className="text-sm text-muted-foreground mb-2">Blocked Today</p>
              <p className="text-4xl font-bold text-green-500">18</p>
              <p className="text-xs text-muted-foreground mt-2">Prevented attacks</p>
            </div>
          </div>

          {/* Threats Table */}
          <div className="border border-[#262626] rounded-lg bg-[#141414] overflow-hidden">
            <div className="p-6 border-b border-[#262626]">
              <h2 className="text-xl font-semibold text-foreground">Threat Queue</h2>
            </div>
            <div className="space-y-0">
              {threats.map((threat) => (
                <div
                  key={threat.id}
                  className="p-6 border-b border-[#262626] last:border-0 hover:bg-[#1a1a1a] transition-colors cursor-pointer"
                >
                  <div className="flex items-start justify-between gap-6">
                    <div className="flex-1 space-y-2">
                      <div className="flex items-center gap-3">
                        <AlertTriangle className="w-5 h-5 text-destructive" />
                        <h3 className="font-semibold text-foreground">{threat.title}</h3>
                        <Badge className={`${severityColor[threat.severity]} border`}>
                          {threat.severity}
                        </Badge>
                        <Badge className={`${statusColor[threat.status]} border`}>
                          {threat.status}
                        </Badge>
                      </div>
                      <p className="text-sm text-muted-foreground ml-8">{threat.description}</p>
                      
                      <div className="flex items-center gap-6 ml-8 mt-3 text-sm text-muted-foreground">
                        <div className="flex items-center gap-2">
                          <MapPin className="w-4 h-4" />
                          <span>{threat.source}</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <User className="w-4 h-4" />
                          <span>{threat.user}</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <Clock className="w-4 h-4" />
                          <span>{threat.time}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </main>
      </div>
    </div>
  )
}
