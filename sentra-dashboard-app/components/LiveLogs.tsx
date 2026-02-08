'use client'

import { useEffect, useRef } from 'react'
import type { AgentLog } from '@/hooks/useAgentState'

interface LiveLogsProps {
  logs: AgentLog[]
}

export function LiveLogs({ logs }: LiveLogsProps) {
  const scrollRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [logs])

  const getLevelColor = (level: AgentLog['level']) => {
    switch (level) {
      case 'CRITICAL':
        return 'text-destructive'
      case 'WARNING':
        return 'text-yellow-500'
      case 'SUCCESS':
        return 'text-green-500'
      case 'DEBUG':
        return 'text-blue-400'
      default:
        return 'text-cyan-400'
    }
  }

  const getLevelBg = (level: AgentLog['level']) => {
    switch (level) {
      case 'CRITICAL':
        return 'bg-red-500/10'
      case 'WARNING':
        return 'bg-yellow-500/10'
      case 'SUCCESS':
        return 'bg-green-500/10'
      default:
        return 'bg-blue-500/10'
    }
  }

  return (
    <div
      ref={scrollRef}
      className="h-96 overflow-y-auto bg-[#0a0a0a] border border-[#262626] rounded-lg p-4 space-y-1 font-mono text-xs"
    >
      {logs.length === 0 ? (
        <div className="text-muted-foreground text-center py-20">Waiting for agent activity...</div>
      ) : (
        logs.map((log, i) => (
          <div key={i} className={`flex gap-3 p-2 rounded ${getLevelBg(log.level)}`}>
            <span className="text-muted-foreground flex-shrink-0">{new Date(log.timestamp).toLocaleTimeString()}</span>
            <span className={`font-semibold flex-shrink-0 w-10 ${getLevelColor(log.level)}`}>{log.level}</span>
            <span className="text-muted-foreground flex-shrink-0 max-w-xs truncate">{log.component}</span>
            <span className="text-foreground flex-1">{log.message}</span>
          </div>
        ))
      )}
    </div>
  )
}
