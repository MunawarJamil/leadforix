import * as React from 'react'
import { motion, useInView, useReducedMotion } from 'motion/react'
import { MapPin } from 'lucide-react'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { ScoreGauge } from '@/components/widgets/score-gauge'
import { cn } from '@/lib/utils'

export interface LeadCardData {
  id: string
  role: string
  company: string
  location: string
  tags: readonly string[]
  score: number
}

export interface LeadCardProps {
  lead: LeadCardData
  /** Optional className passthrough for layout (float, rotate, etc.). */
  className?: string
  /** Delay before the score starts counting up. */
  scoreDelay?: number
  /** Disable the count-up (e.g. for marquee-style clones). */
  static?: boolean
  /** Enable glowing snake border around the card. */
  withSnakeBorder?: boolean
}

export function LeadCard({
  lead,
  className,
  scoreDelay = 0,
  static: isStatic,
}: LeadCardProps) {
  const ref = React.useRef<HTMLDivElement>(null)
  const inView = useInView(ref, { once: true, margin: '-40px' })
  const prefersReduced = useReducedMotion()

  // Drive the score from 0 to target. ScoreGauge's own CSS transition
  // handles the visual interpolation, so we just step the value.
  const [score, setScore] = React.useState(isStatic || prefersReduced ? lead.score : 0)

  React.useEffect(() => {
    if (isStatic || prefersReduced) return
    if (!inView) return

    const timeout = window.setTimeout(() => setScore(lead.score), scoreDelay * 1000)
    return () => window.clearTimeout(timeout)
  }, [inView, lead.score, scoreDelay, isStatic, prefersReduced])

  // Dynamic visual accents based on match score
  const isTopMatch = lead.score >= 90
  const beaconColor = isTopMatch ? 'bg-emerald-400' : 'bg-accent'
  const beamGradient = isTopMatch
    ? 'from-transparent via-emerald-400/90 to-transparent'
    : 'from-transparent via-accent/80 to-transparent'
  const glowBg = isTopMatch
    ? 'radial-gradient(circle, rgb(16 185 129 / 0.18) 0%, transparent 70%)'
    : 'radial-gradient(circle, rgb(99 102 241 / 0.18) 0%, transparent 70%)'

  return (
    <Card
      ref={ref}
      className={cn(
        'group relative overflow-hidden w-full max-w-sm p-5 shadow-card bg-surface/95 backdrop-blur-sm',
        'border border-border hover:border-border-strong',
        'transition-all duration-300 ease-out hover:-translate-y-1.5 hover:shadow-glow',
        className
      )}
    >
      {/* Top glowing gradient accent beam */}
      <div
        aria-hidden="true"
        className={cn(
          'pointer-events-none absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r',
          beamGradient,
          'opacity-70 group-hover:opacity-100 transition-opacity duration-300'
        )}
      />

      {/* Subtle ambient corner backlight on hover */}
      <div
        aria-hidden="true"
        className="pointer-events-none absolute -top-10 -right-10 h-32 w-32 rounded-full blur-2xl opacity-20 group-hover:opacity-50 transition-opacity duration-500"
        style={{ background: glowBg }}
      />

      <div className="relative z-10">
        <div className="flex items-start justify-between gap-3 mb-2.5">
          <div className="min-w-0">
            <div className="flex items-center gap-2 mb-0.5">
              {/* Live signal beacon */}
              <span className="relative flex h-2 w-2 shrink-0" title="Active live lead">
                <span
                  className={cn(
                    'animate-ping absolute inline-flex h-full w-full rounded-full opacity-75',
                    beaconColor
                  )}
                />
                <span className={cn('relative inline-flex rounded-full h-2 w-2', beaconColor)} />
              </span>
              <h3 className="text-sm font-semibold text-text-primary truncate">{lead.role}</h3>
            </div>
            <p className="text-xs text-text-secondary truncate pl-4">{lead.company}</p>
          </div>
        </div>

        <div className="flex items-center gap-1.5 text-[11px] text-text-muted mb-4 pl-4">
          <MapPin className="w-3 h-3" />
          <span className="truncate">{lead.location}</span>
        </div>

        <div className="flex flex-wrap gap-1.5 mb-4 pl-4">
          {lead.tags.map((tag) => (
            <Badge key={tag} variant="secondary" size="sm" className="font-mono">
              {tag}
            </Badge>
          ))}
        </div>

        <div className="pl-4">
          <ScoreGauge score={score} size="sm" />
        </div>
      </div>
    </Card>
  )
}

/** A version that floats gently — used in the hero preview cluster. */
export function FloatingLeadCard(props: LeadCardProps) {
  const prefersReduced = useReducedMotion()
  return (
    <motion.div
      animate={prefersReduced ? undefined : { y: [0, -8, 0] }}
      transition={{ duration: 6, repeat: Infinity, ease: 'easeInOut' }}
      className="will-change-transform"
    >
      <LeadCard {...props} />
    </motion.div>
  )
}