'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { LayoutDashboard, AlertTriangle, BarChart3, MessageSquare, Zap, Settings, Shield } from 'lucide-react'

const navItems = [
  { href: '/', label: 'Dashboard', icon: LayoutDashboard },
  { href: '/threats', label: 'Active Threats', icon: AlertTriangle },
  { href: '/analytics', label: 'Analytics', icon: BarChart3 },
  { href: '/incidents', label: 'Incidents', icon: Zap },
  { href: '/chat', label: 'AI Chat', icon: MessageSquare },
  { href: '/settings', label: 'Settings', icon: Settings },
]

export function Sidebar() {
  const pathname = usePathname()

  return (
    <aside className="fixed left-0 top-0 h-screen w-64 border-r border-border bg-[#0f0f0f] p-6 flex flex-col">
      <div className="flex items-center gap-3 mb-8">
        <div className="w-8 h-8 rounded bg-primary flex items-center justify-center">
          <Shield className="w-5 h-5 text-primary-foreground" />
        </div>
        <h1 className="text-xl font-bold text-foreground">SENTRA</h1>
      </div>

      <nav className="flex-1 space-y-2">
        {navItems.map((item) => {
          const Icon = item.icon
          const isActive = pathname === item.href
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                isActive
                  ? 'bg-[#262626] text-primary'
                  : 'text-muted-foreground hover:text-foreground hover:bg-[#1a1a1a]'
              }`}
            >
              <Icon className="w-5 h-5" />
              <span className="text-sm font-medium">{item.label}</span>
            </Link>
          )
        })}
      </nav>

      <div className="pt-4 border-t border-[#1a1a1a]">
        <div className="text-xs text-muted-foreground">
          <p className="font-semibold mb-2">Status</p>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
            <span>Systems Active</span>
          </div>
        </div>
      </div>
    </aside>
  )
}
