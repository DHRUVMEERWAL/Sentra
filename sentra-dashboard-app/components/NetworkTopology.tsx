'use client'

import React from "react"

import { useState, useEffect, useRef } from 'react'
import { Camera, HardDrive, Laptop, AlertTriangle, Activity } from 'lucide-react'

interface Device {
  id: string
  name: string
  type: 'ipcam' | 'nas' | 'laptop'
  x: number
  y: number
  icon: React.ReactNode
  status: 'normal' | 'suspicious' | 'compromised'
  activity: number
}

interface Link {
  source: string
  target: string
  active: boolean
  dataVolume: number
}

export function NetworkTopology() {
  const svgRef = useRef<SVGSVGElement>(null)
  const [devices, setDevices] = useState<Device[]>([
    {
      id: 'ipcam',
      name: 'IP Camera',
      type: 'ipcam',
      x: 150,
      y: 150,
      icon: <Camera className="w-5 h-5" />,
      status: 'normal',
      activity: 0,
    },
    {
      id: 'nas',
      name: 'SSH NAS',
      type: 'nas',
      x: 350,
      y: 150,
      icon: <HardDrive className="w-5 h-5" />,
      status: 'suspicious',
      activity: 0,
    },
    {
      id: 'laptop',
      name: 'Laptop',
      type: 'laptop',
      x: 250,
      y: 300,
      icon: <Laptop className="w-5 h-5" />,
      status: 'normal',
      activity: 0,
    },
  ])

  const [links, setLinks] = useState<Link[]>([
    { source: 'ipcam', target: 'nas', active: false, dataVolume: 0 },
    { source: 'nas', target: 'laptop', active: false, dataVolume: 0 },
    { source: 'laptop', target: 'ipcam', active: false, dataVolume: 0 },
  ])

  // Simulate network activity
  useEffect(() => {
    const interval = setInterval(() => {
      const activeLink = Math.floor(Math.random() * links.length)
      const threatDetected = Math.random() > 0.7

      setLinks((prev) =>
        prev.map((link, idx) => ({
          ...link,
          active: idx === activeLink,
          dataVolume: idx === activeLink ? Math.random() * 100 : 0,
        }))
      )

      // Simulate device status changes based on threat
      if (threatDetected) {
        setDevices((prev) =>
          prev.map((device) => {
            if (device.id === links[activeLink].source || device.id === links[activeLink].target) {
              return {
                ...device,
                status: Math.random() > 0.5 ? 'suspicious' : 'normal',
                activity: Math.random() * 100,
              }
            }
            return device
          })
        )
      }
    }, 2000)

    return () => clearInterval(interval)
  }, [links])

  const getDeviceColor = (status: string) => {
    switch (status) {
      case 'compromised':
        return '#ef4444'
      case 'suspicious':
        return '#f59e0b'
      default:
        return '#06b6d4'
    }
  }

  const getStatusText = (status: string) => {
    switch (status) {
      case 'compromised':
        return 'COMPROMISED'
      case 'suspicious':
        return 'SUSPICIOUS'
      default:
        return 'NORMAL'
    }
  }

  return (
    <div className="p-6 border border-[#262626] rounded-lg bg-[#141414]">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-foreground">Network Topology</h3>
        <p className="text-xs text-muted-foreground">172.18.0.2</p>
      </div>

      <svg
        ref={svgRef}
        width="100%"
        height={400}
        viewBox="0 0 500 400"
        className="border border-[#262626] rounded bg-[#0a0a0a]"
        style={{ background: '#0a0a0a' }}
      >
        {/* Connection lines */}
        <defs>
          <marker
            id="arrowActive"
            markerWidth="10"
            markerHeight="10"
            refX="5"
            refY="5"
            orient="auto"
          >
            <path d="M 0 0 L 10 5 L 0 10" fill="#06b6d4" />
          </marker>
          <marker
            id="arrowInactive"
            markerWidth="10"
            markerHeight="10"
            refX="5"
            refY="5"
            orient="auto"
          >
            <path d="M 0 0 L 10 5 L 0 10" fill="#525252" />
          </marker>
        </defs>

        {/* Draw links */}
        {links.map((link, idx) => {
          const source = devices.find((d) => d.id === link.source)
          const target = devices.find((d) => d.id === link.target)
          if (!source || !target) return null

          return (
            <g key={`link-${idx}`}>
              {/* Background line */}
              <line
                x1={source.x}
                y1={source.y}
                x2={target.x}
                y2={target.y}
                stroke={link.active ? '#06b6d4' : '#262626'}
                strokeWidth={link.active ? 2 : 1}
                opacity={link.active ? 0.8 : 0.3}
                markerEnd={link.active ? 'url(#arrowActive)' : 'url(#arrowInactive)'}
              />
              {/* Data flow animation */}
              {link.active && (
                <circle
                  cx={source.x + (target.x - source.x) * 0.5}
                  cy={source.y + (target.y - source.y) * 0.5}
                  r="4"
                  fill="#06b6d4"
                  opacity="0.8"
                  style={{
                    animation: 'pulse 1s ease-in-out infinite',
                  }}
                />
              )}
              {/* Data volume label */}
              {link.active && (
                <text
                  x={source.x + (target.x - source.x) * 0.5}
                  y={source.y + (target.y - source.y) * 0.5 - 10}
                  fill="#a3a3a3"
                  fontSize="10"
                  textAnchor="middle"
                >
                  {link.dataVolume.toFixed(0)} MB/s
                </text>
              )}
            </g>
          )
        })}

        {/* Draw devices */}
        {devices.map((device) => (
          <g key={device.id}>
            {/* Outer ring for activity */}
            {device.activity > 0 && (
              <circle
                cx={device.x}
                cy={device.y}
                r={40}
                fill="none"
                stroke={getDeviceColor(device.status)}
                strokeWidth="2"
                opacity="0.3"
                style={{
                  animation: device.status === 'suspicious' ? 'pulse 0.6s ease-in-out infinite' : 'none',
                }}
              />
            )}

            {/* Device circle */}
            <circle
              cx={device.x}
              cy={device.y}
              r="28"
              fill="#141414"
              stroke={getDeviceColor(device.status)}
              strokeWidth="2"
              style={{
                filter: device.status === 'suspicious' ? 'drop-shadow(0 0 8px rgba(245, 158, 11, 0.6))' : 'none',
              }}
            />

            {/* Status indicator dot */}
            <circle
              cx={device.x + 20}
              cy={device.y - 20}
              r="6"
              fill={getDeviceColor(device.status)}
              stroke="#0a0a0a"
              strokeWidth="2"
            />

            {/* Device name label */}
            <text
              x={device.x}
              y={device.y + 50}
              fill="#fafafa"
              fontSize="12"
              fontWeight="600"
              textAnchor="middle"
              fontFamily="monospace"
            >
              {device.name}
            </text>

            {/* Status label */}
            <text
              x={device.x}
              y={device.y + 65}
              fill={getDeviceColor(device.status)}
              fontSize="10"
              textAnchor="middle"
              fontFamily="monospace"
            >
              {getStatusText(device.status)}
            </text>
          </g>
        ))}
      </svg>

      {/* Device Legend */}
      <div className="mt-6 grid grid-cols-3 gap-4">
        {devices.map((device) => (
          <div
            key={device.id}
            className="p-3 border border-[#262626] rounded bg-[#0a0a0a] hover:border-[#404040] transition-colors"
          >
            <div className="flex items-center gap-2 mb-2">
              <div className="text-primary">{device.icon}</div>
              <p className="text-xs font-semibold text-foreground">{device.name}</p>
            </div>
            <p className="text-xs text-muted-foreground">172.18.0.2</p>
            <div className="flex items-center gap-1 mt-2">
              <div
                className="w-2 h-2 rounded-full"
                style={{ backgroundColor: getDeviceColor(device.status) }}
              />
              <p className="text-xs text-muted-foreground">{getStatusText(device.status)}</p>
            </div>
            {device.activity > 0 && (
              <p className="text-xs text-primary mt-1">Activity: {device.activity.toFixed(0)}%</p>
            )}
          </div>
        ))}
      </div>

      <style jsx>{`
        @keyframes pulse {
          0% {
            opacity: 1;
          }
          50% {
            opacity: 0.3;
          }
          100% {
            opacity: 1;
          }
        }
      `}</style>
    </div>
  )
}
