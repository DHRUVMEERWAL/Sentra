'use client'

import { useState } from 'react'
import { Sidebar } from '@/components/Sidebar'
import { PageHeader } from '@/components/PageHeader'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Send } from 'lucide-react'

const initialMessages = [
  {
    id: 1,
    sender: 'AI Analyst',
    message: 'Hello! I\'m SENTRA\'s AI Analyst. I can help you analyze threats, investigate incidents, and provide security insights. What would you like to know?',
    timestamp: '10:30 AM',
  },
  {
    id: 2,
    sender: 'You',
    message: 'What are the current active threats?',
    timestamp: '10:31 AM',
  },
  {
    id: 3,
    sender: 'AI Analyst',
    message: 'Based on real-time analysis, we have 1 critical threat currently active. There\'s a honeypot engagement detected in Deception-Network-1. The intruder has been trapped and is being monitored. We\'re collecting behavioral data while keeping systems safe.',
    timestamp: '10:31 AM',
  },
  {
    id: 4,
    sender: 'You',
    message: 'What\'s the threat attribution status?',
    timestamp: '10:32 AM',
  },
  {
    id: 5,
    sender: 'AI Analyst',
    message: 'The threat has been partially attributed. Initial analysis suggests insider threat characteristics: internal IP origin (192.168.1.x), legitimate credentials used, and knowledge of sensitive file locations. Recommend escalating to CIRT for full investigation.',
    timestamp: '10:33 AM',
  },
]

export default function ChatPage() {
  const [messages, setMessages] = useState(initialMessages)
  const [input, setInput] = useState('')

  const handleSendMessage = () => {
    if (!input.trim()) return

    const newMessage = {
      id: messages.length + 1,
      sender: 'You',
      message: input,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    }

    setMessages([...messages, newMessage])
    setInput('')

    // Simulate AI response
    setTimeout(() => {
      const responses = [
        'That\'s an important question. Let me analyze the current threat landscape for you.',
        'Based on the latest intelligence, the threat profile indicates...',
        'I\'ve identified several patterns in the recent activity that warrant investigation.',
        'That matches with our current threat model. Here\'s what we\'ve detected...',
        'Excellent question. The data suggests this is a targeted attack vector.',
      ]

      const aiMessage = {
        id: messages.length + 2,
        sender: 'AI Analyst',
        message: responses[Math.floor(Math.random() * responses.length)],
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      }

      setMessages(prev => [...prev, aiMessage])
    }, 1000)
  }

  return (
    <div className="flex min-h-screen bg-background">
      <Sidebar />
      <div className="flex-1 ml-64">
        <PageHeader 
          title="AI Security Analyst" 
          description="Chat with SENTRA's AI-powered security analyst"
        />
        
        <main className="p-8 flex flex-col h-[calc(100vh-120px)]">
          <div className="flex-1 border border-[#262626] rounded-lg bg-[#141414] flex flex-col overflow-hidden">
            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-6 space-y-4">
              {messages.map((msg) => (
                <div
                  key={msg.id}
                  className={`flex gap-4 ${msg.sender === 'You' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-xl px-4 py-3 rounded-lg ${
                      msg.sender === 'You'
                        ? 'bg-primary text-primary-foreground'
                        : 'bg-[#1a1a1a] text-foreground border border-[#262626]'
                    }`}
                  >
                    {msg.sender !== 'You' && (
                      <p className="text-xs font-semibold text-muted-foreground mb-1">{msg.sender}</p>
                    )}
                    <p className="text-sm">{msg.message}</p>
                    <p className={`text-xs mt-1 ${
                      msg.sender === 'You'
                        ? 'text-primary-foreground/70'
                        : 'text-muted-foreground'
                    }`}>
                      {msg.timestamp}
                    </p>
                  </div>
                </div>
              ))}
            </div>

            {/* Input */}
            <div className="border-t border-[#262626] p-6">
              <div className="flex gap-3">
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                  placeholder="Ask about threats, incidents, or analytics..."
                  className="flex-1 px-4 py-2 bg-[#1a1a1a] border border-[#262626] rounded-lg text-foreground placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary"
                />
                <Button
                  onClick={handleSendMessage}
                  className="px-4 py-2 bg-primary hover:bg-primary/90 text-primary-foreground rounded-lg"
                >
                  <Send className="w-4 h-4" />
                </Button>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  )
}
