'use client'

import { Sidebar } from '@/components/Sidebar'
import { PageHeader } from '@/components/PageHeader'
import { Card } from '@/components/ui/card'
import { BarChart, Bar, LineChart, Line, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

const threatsByType = [
  { name: 'Unauthorized Access', value: 28 },
  { name: 'Data Exfiltration', value: 18 },
  { name: 'Privilege Escalation', value: 12 },
  { name: 'Malware', value: 8 },
  { name: 'Others', value: 6 },
]

const weeklyData = [
  { day: 'Mon', threats: 12, blocked: 11, anomalies: 45 },
  { day: 'Tue', threats: 15, blocked: 14, anomalies: 62 },
  { day: 'Wed', threats: 8, blocked: 8, anomalies: 38 },
  { day: 'Thu', threats: 22, blocked: 20, anomalies: 78 },
  { day: 'Fri', threats: 18, blocked: 17, anomalies: 65 },
  { day: 'Sat', threats: 5, blocked: 5, anomalies: 22 },
  { day: 'Sun', threats: 28, blocked: 27, anomalies: 142 },
]

const hourlyData = [
  { hour: '00:00', incidents: 4 },
  { hour: '04:00', incidents: 8 },
  { hour: '08:00', incidents: 12 },
  { hour: '12:00', incidents: 18 },
  { hour: '16:00', incidents: 24 },
  { hour: '20:00', incidents: 28 },
  { hour: '23:00', incidents: 15 },
]

const colors = ['#06b6d4', '#8b5cf6', '#f59e0b', '#10b981', '#ef4444']

export default function AnalyticsPage() {
  return (
    <div className="flex min-h-screen bg-background">
      <Sidebar />
      <div className="flex-1 ml-64">
        <PageHeader 
          title="Analytics & Insights" 
          description="Detailed analysis of security events and trends"
        />
        
        <div className="p-8 space-y-8">
          {/* Key Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="p-6 border border-[#262626] rounded-lg bg-[#141414]">
              <p className="text-sm text-muted-foreground mb-2">Total Incidents</p>
              <p className="text-4xl font-bold text-foreground">108</p>
              <p className="text-xs text-green-500 mt-2">↓ 5% from last week</p>
            </div>
            <div className="p-6 border border-[#262626] rounded-lg bg-[#141414]">
              <p className="text-sm text-muted-foreground mb-2">Block Rate</p>
              <p className="text-4xl font-bold text-primary">96.3%</p>
              <p className="text-xs text-muted-foreground mt-2">Successfully stopped</p>
            </div>
            <div className="p-6 border border-[#262626] rounded-lg bg-[#141414]">
              <p className="text-sm text-muted-foreground mb-2">Avg Response Time</p>
              <p className="text-4xl font-bold text-secondary">2.3s</p>
              <p className="text-xs text-muted-foreground mt-2">From detection</p>
            </div>
            <div className="p-6 border border-[#262626] rounded-lg bg-[#141414]">
              <p className="text-sm text-muted-foreground mb-2">Risk Score</p>
              <p className="text-4xl font-bold text-destructive">24</p>
              <p className="text-xs text-muted-foreground mt-2">Current level</p>
            </div>
          </div>

          {/* Charts Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="p-6 border border-[#262626] rounded-lg bg-[#141414]">
              <h3 className="text-lg font-semibold text-foreground mb-4">Weekly Activity</h3>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={weeklyData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#262626" />
                  <XAxis dataKey="day" stroke="#a3a3a3" />
                  <YAxis stroke="#a3a3a3" />
                  <Tooltip contentStyle={{ backgroundColor: '#1a1a1a', border: '1px solid #262626' }} />
                  <Legend />
                  <Bar dataKey="threats" fill="#ef4444" name="Threats Detected" />
                  <Bar dataKey="blocked" fill="#10b981" name="Blocked" />
                </BarChart>
              </ResponsiveContainer>
            </div>

            <div className="p-6 border border-[#262626] rounded-lg bg-[#141414]">
              <h3 className="text-lg font-semibold text-foreground mb-4">Threat Distribution</h3>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={threatsByType}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={90}
                    paddingAngle={5}
                    dataKey="value"
                  >
                    {threatsByType.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
                    ))}
                  </Pie>
                  <Tooltip contentStyle={{ backgroundColor: '#1a1a1a', border: '1px solid #262626' }} />
                </PieChart>
              </ResponsiveContainer>
              <div className="mt-4 space-y-2">
                {threatsByType.map((item, i) => (
                  <div key={i} className="flex items-center gap-3 text-sm">
                    <div className="w-3 h-3 rounded-full" style={{ backgroundColor: colors[i] }} />
                    <span className="text-muted-foreground flex-1">{item.name}</span>
                    <span className="font-semibold text-foreground">{item.value}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Hourly Trend */}
          <div className="p-6 border border-[#262626] rounded-lg bg-[#141414]">
            <h3 className="text-lg font-semibold text-foreground mb-4">24-Hour Incident Trend</h3>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={hourlyData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#262626" />
                <XAxis dataKey="hour" stroke="#a3a3a3" />
                <YAxis stroke="#a3a3a3" />
                <Tooltip contentStyle={{ backgroundColor: '#1a1a1a', border: '1px solid #262626' }} />
                <Line
                  type="monotone"
                  dataKey="incidents"
                  stroke="#06b6d4"
                  strokeWidth={3}
                  dot={{ fill: '#06b6d4', r: 5 }}
                  activeDot={{ r: 7 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Insights */}
          <div className="p-6 border border-[#262626] rounded-lg bg-[#141414]">
            <h3 className="text-lg font-semibold text-foreground mb-4">Key Insights</h3>
            <div className="space-y-4">
              <div className="flex gap-4 p-4 bg-[#1a1a1a] rounded-lg">
                <div className="w-2 h-2 rounded-full bg-primary mt-1 flex-shrink-0" />
                <div>
                  <p className="text-sm font-medium text-foreground">Peak Activity Window</p>
                  <p className="text-sm text-muted-foreground">Threat activity peaks between 16:00-22:00 UTC</p>
                </div>
              </div>
              <div className="flex gap-4 p-4 bg-[#1a1a1a] rounded-lg">
                <div className="w-2 h-2 rounded-full bg-primary mt-1 flex-shrink-0" />
                <div>
                  <p className="text-sm font-medium text-foreground">Peak Activity Window</p>
                  <p className="text-sm text-muted-foreground">Threat activity peaks between 16:00-22:00 UTC</p>
                </div>
              </div>
              <div className="flex gap-4 p-4 bg-[#1a1a1a] rounded-lg">
                <div className="w-2 h-2 rounded-full bg-primary mt-1 flex-shrink-0" />
                <div>
                  <p className="text-sm font-medium text-foreground">Most Common Attack Vector</p>
                  <p className="text-sm text-muted-foreground">Unauthorized access attempts (26% of all incidents)</p>
                </div>
              </div>
              <div className="flex gap-4 p-4 bg-[#1a1a1a] rounded-lg">
                <div className="w-2 h-2 rounded-full bg-primary mt-1 flex-shrink-0" />
                <div>
                  <p className="text-sm font-medium text-foreground">System Effectiveness</p>
                  <p className="text-sm text-muted-foreground">96.3% block rate maintained over 7 days</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
