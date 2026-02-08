'use client'

import { Bell, Search } from 'lucide-react'
import { Button } from '@/components/ui/button'

interface PageHeaderProps {
  title: string
  description?: string
}

export function PageHeader({ title, description }: PageHeaderProps) {
  return (
    <div className="border-b border-[#262626] bg-[#0a0a0a] sticky top-0 z-10">
      <div className="flex items-center justify-between px-8 py-6">
        <div className="flex-1">
          <h1 className="text-3xl font-bold text-foreground mb-1">{title}</h1>
          {description && <p className="text-sm text-muted-foreground">{description}</p>}
        </div>
        <div className="flex items-center gap-4">
          <div className="relative hidden md:block">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <input
              placeholder="Search..."
              className="pl-10 pr-4 py-2 bg-[#1a1a1a] border border-[#262626] rounded-lg text-sm text-foreground placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary"
            />
          </div>
          <Button variant="outline" size="icon" className="border-[#262626] bg-transparent">
            <Bell className="w-4 h-4" />
          </Button>
        </div>
      </div>
    </div>
  )
}
