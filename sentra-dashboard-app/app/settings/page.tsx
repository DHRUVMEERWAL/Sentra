'use client'

import { Sidebar } from '@/components/Sidebar'
import { PageHeader } from '@/components/PageHeader'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Toggle } from '@/components/ui/toggle'
import { Bell, Lock, Database, AlertTriangle, Users, Shield } from 'lucide-react'

export default function SettingsPage() {
  return (
    <div className="flex min-h-screen bg-background">
      <Sidebar />
      <div className="flex-1 ml-64">
        <PageHeader 
          title="Settings" 
          description="Configure SENTRA system preferences"
        />
        
        <main className="p-8 space-y-8">
          {/* Notifications */}
          <div className="border border-[#262626] rounded-lg bg-[#141414] overflow-hidden">
            <div className="p-6 border-b border-[#262626] flex items-start justify-between">
              <div className="flex items-start gap-3">
                <Bell className="w-5 h-5 text-primary mt-1" />
                <div>
                  <h3 className="font-semibold text-foreground">Notifications</h3>
                  <p className="text-sm text-muted-foreground mt-1">Manage alert preferences</p>
                </div>
              </div>
            </div>
            <div className="p-6 space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium text-foreground">Critical Alerts</p>
                  <p className="text-sm text-muted-foreground">Receive notifications for critical threats</p>
                </div>
                <Toggle defaultChecked className="bg-primary" />
              </div>
              <div className="border-t border-[#262626] pt-6 flex items-center justify-between">
                <div>
                  <p className="font-medium text-foreground">Email Notifications</p>
                  <p className="text-sm text-muted-foreground">Send alerts to registered email</p>
                </div>
                <Toggle defaultChecked className="bg-primary" />
              </div>
              <div className="border-t border-[#262626] pt-6 flex items-center justify-between">
                <div>
                  <p className="font-medium text-foreground">Slack Integration</p>
                  <p className="text-sm text-muted-foreground">Post alerts to Slack channel</p>
                </div>
                <Toggle className="bg-[#1a1a1a]" />
              </div>
            </div>
          </div>

          {/* Security */}
          <div className="border border-[#262626] rounded-lg bg-[#141414] overflow-hidden">
            <div className="p-6 border-b border-[#262626] flex items-start justify-between">
              <div className="flex items-start gap-3">
                <Lock className="w-5 h-5 text-primary mt-1" />
                <div>
                  <h3 className="font-semibold text-foreground">Security</h3>
                  <p className="text-sm text-muted-foreground mt-1">Manage access and authentication</p>
                </div>
              </div>
            </div>
            <div className="p-6 space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium text-foreground">Two-Factor Authentication</p>
                  <p className="text-sm text-muted-foreground">Enabled for all admin accounts</p>
                </div>
                <Toggle defaultChecked className="bg-primary" />
              </div>
              <div className="border-t border-[#262626] pt-6 flex items-center justify-between">
                <div>
                  <p className="font-medium text-foreground">IP Whitelisting</p>
                  <p className="text-sm text-muted-foreground">Restrict access to specific IPs</p>
                </div>
                <Toggle defaultChecked className="bg-primary" />
              </div>
              <div className="border-t border-[#262626] pt-6">
                <p className="font-medium text-foreground mb-3">Session Timeout</p>
                <select className="w-full px-4 py-2 bg-[#1a1a1a] border border-[#262626] rounded-lg text-foreground focus:outline-none focus:ring-2 focus:ring-primary">
                  <option>15 minutes</option>
                  <option>30 minutes</option>
                  <option>1 hour</option>
                  <option>Never</option>
                </select>
              </div>
            </div>
          </div>

          {/* Data Management */}
          <div className="border border-[#262626] rounded-lg bg-[#141414] overflow-hidden">
            <div className="p-6 border-b border-[#262626] flex items-start justify-between">
              <div className="flex items-start gap-3">
                <Database className="w-5 h-5 text-primary mt-1" />
                <div>
                  <h3 className="font-semibold text-foreground">Data Management</h3>
                  <p className="text-sm text-muted-foreground mt-1">Control data retention and backups</p>
                </div>
              </div>
            </div>
            <div className="p-6 space-y-6">
              <div>
                <div className="flex items-center justify-between mb-2">
                  <p className="font-medium text-foreground">Log Retention</p>
                  <span className="text-sm text-muted-foreground">90 days</span>
                </div>
                <input
                  type="range"
                  min="30"
                  max="365"
                  defaultValue="90"
                  className="w-full"
                />
              </div>
              <div className="border-t border-[#262626] pt-6 flex items-center justify-between">
                <div>
                  <p className="font-medium text-foreground">Automatic Backups</p>
                  <p className="text-sm text-muted-foreground">Daily at 02:00 UTC</p>
                </div>
                <Toggle defaultChecked className="bg-primary" />
              </div>
              <div className="border-t border-[#262626] pt-6">
                <Button className="bg-primary hover:bg-primary/90 text-primary-foreground">
                  Export Incident Data
                </Button>
              </div>
            </div>
          </div>

          {/* Threat Rules */}
          <div className="border border-[#262626] rounded-lg bg-[#141414] overflow-hidden">
            <div className="p-6 border-b border-[#262626] flex items-start justify-between">
              <div className="flex items-start gap-3">
                <AlertTriangle className="w-5 h-5 text-primary mt-1" />
                <div>
                  <h3 className="font-semibold text-foreground">Threat Rules</h3>
                  <p className="text-sm text-muted-foreground mt-1">Configure detection sensitivity</p>
                </div>
              </div>
            </div>
            <div className="p-6 space-y-6">
              <div>
                <div className="flex items-center justify-between mb-2">
                  <p className="font-medium text-foreground">Sensitivity Level</p>
                  <span className="text-sm font-mono text-primary">High</span>
                </div>
                <div className="flex gap-2">
                  <Button variant="outline" size="sm" className="border-[#262626] bg-transparent">Low</Button>
                  <Button variant="outline" size="sm" className="border-[#262626] bg-transparent">Medium</Button>
                  <Button size="sm" className="bg-primary text-primary-foreground">High</Button>
                </div>
              </div>
              <div className="border-t border-[#262626] pt-6 flex items-center justify-between">
                <div>
                  <p className="font-medium text-foreground">Machine Learning Detection</p>
                  <p className="text-sm text-muted-foreground">Enable AI-powered anomaly detection</p>
                </div>
                <Toggle defaultChecked className="bg-primary" />
              </div>
            </div>
          </div>

          {/* System */}
          <div className="border border-[#262626] rounded-lg bg-[#141414] overflow-hidden">
            <div className="p-6 border-b border-[#262626] flex items-start justify-between">
              <div className="flex items-start gap-3">
                <Shield className="w-5 h-5 text-primary mt-1" />
                <div>
                  <h3 className="font-semibold text-foreground">System</h3>
                  <p className="text-sm text-muted-foreground mt-1">General system configuration</p>
                </div>
              </div>
            </div>
            <div className="p-6 space-y-6">
              <div className="grid grid-cols-2 gap-6">
                <div>
                  <p className="text-sm text-muted-foreground mb-1">System Version</p>
                  <p className="font-mono text-foreground">v2.4.1</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground mb-1">Last Update</p>
                  <p className="text-foreground">Jan 15, 2026</p>
                </div>
              </div>
              <div className="border-t border-[#262626] pt-6 flex gap-3">
                <Button variant="outline" className="border-[#262626] bg-transparent">Check for Updates</Button>
                <Button variant="outline" className="border-[#262626] bg-transparent">View Logs</Button>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  )
}
