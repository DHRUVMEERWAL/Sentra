'use client'

import { Sidebar } from '@/components/Sidebar'
import { PageHeader } from '@/components/PageHeader'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { CheckCircle, AlertCircle, Clock, User } from 'lucide-react'

const incidents = [
  {
    id: 'INC-001',
    title: 'Honeypot Engagement - System Alpha',
    description: 'Intruder successfully engaged with deception environment',
    status: 'active',
    severity: 'critical',
    startTime: '2 minutes ago',
    duration: '2 min',
    affectedSystems: 'Honeypot-1, Deception-Network',
    assignee: 'Security Team',
  },
  {
    id: 'INC-002',
    title: 'Brute Force Attack Detected',
    description: 'Multiple failed login attempts from external IP',
    status: 'contained',
    severity: 'high',
    startTime: '15 minutes ago',
    duration: '12 min',
    affectedSystems: 'Authentication Service',
    assignee: 'John Doe',
  },
  {
    id: 'INC-003',
    title: 'Unauthorized File Access',
    description: 'Sensitive documents accessed outside normal business hours',
    status: 'resolved',
    severity: 'high',
    startTime: '32 minutes ago',
    duration: '28 min',
    affectedSystems: 'File Server 2, Database 3',
    assignee: 'Sarah Smith',
  },
  {
    id: 'INC-004',
    title: 'Data Transfer Anomaly',
    description: 'Large volume of data being transferred to external location',
    status: 'resolved',
    severity: 'medium',
    startTime: '1 hour ago',
    duration: '45 min',
    affectedSystems: 'Network Gateway',
    assignee: 'Mike Wilson',
  },
  {
    id: 'INC-005',
    title: 'Privilege Escalation Attempt',
    description: 'User attempting to elevate permissions beyond role',
    status: 'resolved',
    severity: 'medium',
    startTime: '2 hours ago',
    duration: '15 min',
    affectedSystems: 'Admin Portal',
    assignee: 'Alex Johnson',
  },
]

const statusIcon = {
  active: <AlertCircle className="w-5 h-5 text-destructive" />,
  contained: <Clock className="w-5 h-5 text-primary" />,
  resolved: <CheckCircle className="w-5 h-5 text-green-500" />,
}

const statusBg = {
  active: 'bg-destructive/10 text-destructive border-destructive/30',
  contained: 'bg-primary/10 text-primary border-primary/30',
  resolved: 'bg-green-500/10 text-green-400 border-green-500/30',
}

const severityBg = {
  critical: 'bg-destructive/10 text-destructive border-destructive/30',
  high: 'bg-warning/10 text-warning border-warning/30',
  medium: 'bg-primary/10 text-primary border-primary/30',
}

export default function IncidentsPage() {
  return (
    <div className="flex min-h-screen bg-background">
      <Sidebar />
      <div className="flex-1 ml-64">
        <PageHeader 
          title="Incident Management" 
          description="Track and manage security incidents across your infrastructure"
        />
        
        <main className="p-8 space-y-6">
          {/* Statistics */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="p-6 border border-[#262626] rounded-lg bg-[#141414]">
              <p className="text-sm text-muted-foreground mb-2">Active Incidents</p>
              <p className="text-4xl font-bold text-destructive">1</p>
              <p className="text-xs text-muted-foreground mt-2">Requires attention</p>
            </div>
            <div className="p-6 border border-[#262626] rounded-lg bg-[#141414]">
              <p className="text-sm text-muted-foreground mb-2">This Week</p>
              <p className="text-4xl font-bold text-warning">12</p>
              <p className="text-xs text-muted-foreground mt-2">Total incidents</p>
            </div>
            <div className="p-6 border border-[#262626] rounded-lg bg-[#141414]">
              <p className="text-sm text-muted-foreground mb-2">Avg Response</p>
              <p className="text-4xl font-bold text-primary">1.8s</p>
              <p className="text-xs text-muted-foreground mt-2">Median time</p>
            </div>
          </div>

          {/* Incidents List */}
          <div className="border border-[#262626] rounded-lg bg-[#141414] overflow-hidden">
            <div className="p-6 border-b border-[#262626]">
              <h2 className="text-xl font-semibold text-foreground">Recent Incidents</h2>
            </div>
            <div className="space-y-0">
              {incidents.map((incident) => (
                <div
                  key={incident.id}
                  className="p-6 border-b border-[#262626] last:border-0 hover:bg-[#1a1a1a] transition-colors"
                >
                  <div className="flex items-start gap-4">
                    <div className="mt-1">
                      {statusIcon[incident.status]}
                    </div>
                    <div className="flex-1">
                      <div className="flex items-start justify-between mb-3">
                        <div>
                          <div className="flex items-center gap-3 mb-1">
                            <span className="text-sm font-mono text-muted-foreground">{incident.id}</span>
                            <h3 className="font-semibold text-foreground text-base">{incident.title}</h3>
                          </div>
                          <p className="text-sm text-muted-foreground">{incident.description}</p>
                        </div>
                        <div className="flex gap-2">
                          <Badge className={`${statusBg[incident.status]} border`}>
                            {incident.status}
                          </Badge>
                          <Badge className={`${severityBg[incident.severity]} border`}>
                            {incident.severity}
                          </Badge>
                        </div>
                      </div>

                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                        <div className="flex items-center gap-2 text-muted-foreground">
                          <Clock className="w-4 h-4" />
                          <span>{incident.startTime}</span>
                        </div>
                        <div className="text-muted-foreground">
                          Duration: <span className="text-foreground">{incident.duration}</span>
                        </div>
                        <div className="text-muted-foreground">
                          Systems: <span className="text-foreground text-xs">{incident.affectedSystems}</span>
                        </div>
                        <div className="flex items-center gap-2 text-muted-foreground">
                          <User className="w-4 h-4" />
                          <span>{incident.assignee}</span>
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
