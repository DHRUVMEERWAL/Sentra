'use client'

import type { AgentState } from '@/hooks/useAgentState'

interface OODACycleProps {
  state: AgentState
  threat: { ip: string; severity: number } | null
}

export function OODACycle({ state, threat }: OODACycleProps) {
  const steps: AgentState[] = ['MONITOR', 'ANALYZE', 'DECIDE', 'DEPLOY']
  const currentIndex = steps.indexOf(state)

  const stepDescriptions: Record<AgentState, string> = {
    MONITOR: 'Observing network traffic and behavioral patterns',
    ANALYZE: 'Analyzing threat data and contextual information',
    DECIDE: 'Reasoning about optimal response strategy',
    DEPLOY: 'Executing deception and containment tactics',
    IDLE: 'Idle',
  }

  return (
    <div className="p-6 border border-[#262626] rounded-lg bg-[#141414] space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-foreground">OODA Cycle</h3>
        <div className="text-sm font-mono">
          <span className="text-primary">{state}</span>
          <span className="text-muted-foreground mx-2">→</span>
          {threat && <span className="text-destructive">{threat.ip}</span>}
        </div>
      </div>

      {/* Cycle visualization */}
      <div className="relative h-40 flex items-center justify-center">
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="w-32 h-32 rounded-full border border-[#262626]" />
        </div>

        <div className="relative w-full flex justify-around px-8">
          {steps.map((step, idx) => {
            const isActive = idx === currentIndex
            const isPast = idx < currentIndex
            return (
              <div key={step} className="flex flex-col items-center gap-2">
                <div
                  className={`w-12 h-12 rounded-full flex items-center justify-center font-mono text-xs font-bold transition-all ${
                    isActive
                      ? 'bg-primary text-primary-foreground scale-125'
                      : isPast
                        ? 'bg-green-500/20 text-green-400 border border-green-500/50'
                        : 'bg-[#1a1a1a] text-muted-foreground border border-[#262626]'
                  }`}
                >
                  {step[0]}
                </div>
                <div className="text-xs text-muted-foreground text-center w-16">{step}</div>
              </div>
            )
          })}
        </div>
      </div>

      {/* Current phase description */}
      <div className="p-4 bg-[#1a1a1a] rounded-lg border border-[#262626]">
        <p className="text-xs text-muted-foreground mb-1">Current Phase:</p>
        <p className="text-sm text-foreground">{stepDescriptions[state]}</p>
        {threat && (
          <div className="mt-3 pt-3 border-t border-[#262626] text-xs space-y-1">
            <p className="text-muted-foreground">
              Threat: <span className="text-destructive font-mono">{threat.ip}</span>
            </p>
            <p className="text-muted-foreground">
              Severity: <span className="text-warning font-mono">{threat.severity}/100</span>
            </p>
          </div>
        )}
      </div>
    </div>
  )
}
