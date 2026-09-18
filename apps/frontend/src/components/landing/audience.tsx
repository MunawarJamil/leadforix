import * as React from 'react'
import { Briefcase, Users } from 'lucide-react'
import { Section } from './section'
import { Badge } from '@/components/ui/badge'
import { Card } from '@/components/ui/card'
import { SnakeBorder } from '@/components/ui/snake-border'
import { ROLES, MORE_ROLES_LABEL } from './data'

interface AudienceCardProps {
  icon: React.ReactNode
  title: string
  body: string
  status: 'live' | 'soon'
}

function AudienceCard({ icon, title, body, status }: AudienceCardProps) {
  const isLive = status === 'live'
  return (
    <Card className="relative overflow-hidden p-6 shadow-card hover:border-border-strong transition-colors">
      <SnakeBorder
        colorFrom={isLive ? '#10B981' : '#6366F1'}
        colorTo={isLive ? '#3B82F6' : '#A78BFA'}
        duration={isLive ? 7.5 : 9}
        size={24}
        strokeWidth={1.5}
      />
      <div className="relative z-10 flex items-start justify-between gap-3 mb-4">
        <div className="flex h-10 w-10 items-center justify-center rounded-lg border border-border bg-surface-hover text-accent">
          {icon}
        </div>
        <Badge variant={isLive ? 'success' : 'secondary'} size="sm" className="font-mono uppercase tracking-wider">
          {isLive ? 'Live' : 'Coming soon'}
        </Badge>
      </div>
      <h3 className="relative z-10 text-lg font-semibold text-text-primary mb-2">{title}</h3>
      <p className="relative z-10 text-sm text-text-secondary leading-relaxed">{body}</p>
    </Card>
  )
}

export function Audience() {
  return (
    <Section className="py-2 sm:py-20">
      <div className="mx-auto max-w-6xl px-6">
        <div className="max-w-2xl mb-14">
          <p className="font-mono text-xs uppercase tracking-[0.25em] text-accent mb-3">
            — Who it's for
          </p>
          <h2 className="text-title text-text-primary">
            Built for people <span className="italic font-serif text-accent">who ship.</span>
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-12">
          <AudienceCard
            icon={<Briefcase className="h-5 w-5" />}
            title="Job seekers"
            body="Find roles that match your skills without scrolling through stale listings or duplicates."
            status="live"
          />
          <AudienceCard
            icon={<Users className="h-5 w-5" />}
            title="Freelancers"
            body="Short-term and contract engagements, scored against your stack. Rolling out soon."
            status="soon"
          />
        </div>

        <div className="flex flex-wrap gap-2">
          {ROLES.map((role) => (
            <span
              key={role}
              className="inline-flex items-center rounded-full border border-border bg-surface px-3 py-1.5 font-mono text-xs text-text-secondary"
            >
              {role}
            </span>
          ))}
          <span className="inline-flex items-center rounded-full border border-dashed border-border-strong bg-transparent px-3 py-1.5 font-mono text-xs text-text-muted">
            {MORE_ROLES_LABEL}
          </span>
        </div>
      </div>
    </Section>
  )
}