import * as React from 'react'
import { motion, useReducedMotion } from 'motion/react'
import { Sparkles, Terminal, MapPin, CheckCircle2, Zap } from 'lucide-react'
import { ScoreGauge } from '@/components/widgets/score-gauge'
import { cn } from '@/lib/utils'

interface SignalItem {
  id: string
  role: string
  company: string
  location: string
  source: 'Hacker News' | 'Remotive' | 'Arbeitnow'
  time: string
  tags: readonly string[]
  score: number
  intent: string
}

const SIGNALS: SignalItem[] = [
  {
    id: 's1',
    role: 'Senior Frontend Engineer',
    company: 'Northwind',
    location: 'Remote · EU',
    source: 'Hacker News',
    time: '6m ago',
    tags: ['React 19', 'TypeScript', 'GraphQL'],
    score: 94,
    intent: 'Direct Engineering Pain',
  },
  {
    id: 's2',
    role: 'Backend Engineer, Platform',
    company: 'Ionis Labs',
    location: 'Hybrid · Berlin',
    source: 'Remotive',
    time: '24m ago',
    tags: ['Go', 'PostgreSQL', 'Kubernetes'],
    score: 87,
    intent: 'Hiring Urgency: High',
  },
  {
    id: 's3',
    role: 'Full-stack Developer',
    company: 'Kestrel',
    location: 'Remote · Global',
    source: 'Arbeitnow',
    time: '1h ago',
    tags: ['Next.js', 'Node.js', 'AWS'],
    score: 81,
    intent: 'Active Pipeline',
  },
]

export function PreviewCards() {
  const prefersReduced = useReducedMotion()
  const [activeRow, setActiveRow] = React.useState<string | null>(SIGNALS[0].id)

  return (
    <div className="relative mx-auto w-full max-w-lg lg:max-w-none">
      {/* Ambient background glow - clipped to bounds on mobile */}
      <div
        aria-hidden="true"
        className="pointer-events-none absolute inset-0 sm:-inset-6 -z-10 rounded-3xl opacity-40 blur-2xl sm:blur-3xl"
        style={{
          background:
            'radial-gradient(ellipse at 50% 50%, rgb(var(--accent) / 0.4), rgb(var(--accent-alt) / 0.15), transparent 70%)',
        }}
      />

      {/* Main Cockpit Frame */}
      <div className="relative overflow-hidden rounded-2xl border border-zinc-800/70 bg-surface/90 backdrop-blur-xl shadow-2xl shadow-black/40 w-full">
        {/* Top Accent Gradient Beam */}
        <div
          aria-hidden="true"
          className="pointer-events-none absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r from-transparent via-accent to-transparent opacity-80"
        />

        {/* Cockpit Window Header */}
        <div className="flex items-center justify-between border-b border-zinc-800/60 bg-background/60 px-3 py-2.5 sm:px-5 sm:py-3 gap-2">
          {/* Left: Window controls & stream label */}
          <div className="flex items-center gap-2 sm:gap-3 min-w-0">
            <div className="flex items-center gap-1.5 shrink-0" aria-hidden="true">
              <span className="h-2 w-2 sm:h-2.5 sm:w-2.5 rounded-full bg-red-500/80" />
              <span className="h-2 w-2 sm:h-2.5 sm:w-2.5 rounded-full bg-amber-500/80" />
              <span className="h-2 w-2 sm:h-2.5 sm:w-2.5 rounded-full bg-emerald-500/80" />
            </div>
            <div className="h-3 w-[1px] bg-zinc-800/60 shrink-0" />
            <div className="flex items-center gap-1.5 text-[11px] sm:text-xs font-mono text-text-secondary truncate">
              <Terminal className="h-3.5 w-3.5 text-accent shrink-0" />
              <span className="font-semibold text-text-primary truncate">signal-stream</span>
              <span className="text-text-muted shrink-0">/live</span>
            </div>
          </div>

          {/* Right: Live Telemetry Indicator */}
          <div className="flex items-center gap-1.5 sm:gap-2 shrink-0">
            <span className="relative flex h-2 w-2 shrink-0">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500" />
            </span>
            <span className="text-[9px] sm:text-[10px] font-mono font-semibold tracking-wider text-emerald-400 uppercase whitespace-nowrap">
              <span className="hidden sm:inline">3 Sources Ingesting</span>
              <span className="inline sm:hidden">3 Sources</span>
            </span>
          </div>
        </div>

        {/* Target Profile Match Bar */}
        <div className="flex flex-wrap items-center justify-between gap-2 border-b border-zinc-800/60 bg-surface-hover/30 px-3 py-2 sm:px-5 sm:py-2.5 text-xs">
          <div className="flex items-center gap-1.5 sm:gap-2 min-w-0">
            <span className="text-text-muted font-mono text-[10px] sm:text-[11px] shrink-0">Matched:</span>
            <span className="font-medium text-text-primary text-[10px] sm:text-xs truncate">
              Fullstack Profile
            </span>
          </div>
          <div className="flex items-center gap-1 text-[9px] sm:text-[10px] font-mono text-accent bg-accent/10 px-2 py-0.5 rounded-md border border-accent/20 shrink-0">
            <Zap className="h-2.5 w-2.5 sm:h-3 sm:w-3" />
            <span>Trigram Dedup</span>
          </div>
        </div>

        {/* Live Signal Feed Stream with thin gray-blackish dividers */}
        <div className="divide-y divide-zinc-800">
          {SIGNALS.map((signal, idx) => {
            const isSelected = activeRow === signal.id
            return (
              <motion.div
                key={signal.id}
                onMouseEnter={() => setActiveRow(signal.id)}
                className={cn(
                  'group relative px-4 sm:px-8 py-5 sm:py-8 transition-all duration-200 cursor-pointer',
                  isSelected ? 'bg-white/[0.035]' : 'hover:bg-white/[0.015]'
                )}
                initial={prefersReduced ? false : { opacity: 0, y: 10 }}
                animate={prefersReduced ? undefined : { opacity: 1, y: 0 }}
                transition={{ duration: 0.4, delay: 0.15 + idx * 0.1 }}
              >
                {/* Active Row Side Accent Indicator */}
                {isSelected && (
                  <div
                    aria-hidden="true"
                    className="absolute left-0 top-0 bottom-0 w-[3px] bg-gradient-to-b from-accent via-accent to-accent-alt"
                  />
                )}

                {/* Role Title, Company & Score Gauge */}
                <div className="flex items-center justify-between gap-3 sm:gap-4 min-w-0">
                  <div className="min-w-0 flex-1">
                    <h4 className="text-sm sm:text-base font-semibold text-text-primary group-hover:text-white transition-colors truncate">
                      {signal.role}
                    </h4>
                    <div className="flex items-center gap-2 mt-1.5 sm:mt-2 text-xs text-text-secondary truncate">
                      <span className="font-medium text-text-primary/90 truncate">{signal.company}</span>
                      <span className="text-text-muted shrink-0">•</span>
                      <div className="flex items-center gap-1 text-text-muted text-[10px] sm:text-[11px] truncate">
                        <MapPin className="h-3 w-3 shrink-0" />
                        <span className="truncate">{signal.location}</span>
                      </div>
                    </div>
                  </div>

                  {/* Match Gauge */}
                  <div className="shrink-0 text-right">
                    <ScoreGauge score={signal.score} size="sm" />
                  </div>
                </div>
              </motion.div>
            )
          })}
        </div>

        {/* Cockpit Terminal Footer */}
        <div className="flex items-center justify-between border-t border-zinc-800/60 bg-background/50 px-3 py-2 sm:px-5 sm:py-2.5 text-[10px] sm:text-[11px] font-mono text-text-muted min-w-0">
          <div className="flex items-center gap-1.5 sm:gap-2 min-w-0">
            <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400 shrink-0" />
            <span className="truncate">Algolia + Remotive + Arbeitnow</span>
          </div>

          <div className="hidden sm:flex items-center gap-1.5 text-text-secondary shrink-0">
            <Sparkles className="h-3 w-3 text-accent" />
            <span>Ready for Agentic Outreach</span>
          </div>
        </div>
      </div>
    </div>
  )
}