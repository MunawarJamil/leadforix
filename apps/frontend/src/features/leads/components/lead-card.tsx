import * as React from 'react'
import { Calendar, ChevronRight, DollarSign, MapPin } from 'lucide-react'
import { Chip } from '@/components/ui/chip'
import { ScoreGauge } from '@/components/widgets/score-gauge'
import { SourcePill } from '@/components/widgets/source-pill'
import { cn } from '@/lib/utils'
import type { Lead } from '../types/lead'

export interface LeadCardProps {
  lead: Lead
  isSelected?: boolean
  onSelect: (lead: Lead) => void
  className?: string
}

export const LeadCard: React.FC<LeadCardProps> = ({
  lead,
  isSelected = false,
  onSelect,
  className,
}) => {
  const visibleSkills = lead.matched_skills.slice(0, 4)
  const remainingSkillsCount = Math.max(0, lead.matched_skills.length - 4)

  const formattedDate = lead.posted_at
    ? new Date(lead.posted_at).toLocaleDateString(undefined, {
        month: 'short',
        day: 'numeric',
      })
    : 'Recent'

  return (
    <div
      onClick={() => onSelect(lead)}
      className={cn(
        'group relative rounded-xl border p-5 bg-surface transition-all duration-200 cursor-pointer',
        'hover:border-accent/40 hover:bg-surface-hover/80 hover:shadow-lg hover:shadow-accent/5',
        isSelected
          ? 'border-accent bg-accent/5 shadow-md shadow-accent/10 ring-1 ring-accent'
          : 'border-border',
        className
      )}
    >
      {/* Header: Company, Source Pill, Score Gauge */}
      <div className="flex items-start justify-between gap-4 mb-3">
        <div className="flex items-center gap-2.5 flex-wrap">
          <span className="font-semibold text-text-primary text-sm tracking-tight">
            {lead.company_name}
          </span>
          <SourcePill source={lead.source} size="sm" />
          {lead.is_remote && (
            <span className="px-2 py-0.5 rounded-full text-[11px] font-medium border border-success/20 bg-success/10 text-success">
              Remote
            </span>
          )}
        </div>
        <ScoreGauge score={lead.match_score} size="sm" />
      </div>

      {/* Role Title */}
      <h3 className="text-base font-bold text-text-primary group-hover:text-accent transition-colors line-clamp-1 mb-2">
        {lead.title}
      </h3>

      {/* Brief Description Snippet */}
      <p className="text-xs text-text-secondary line-clamp-2 leading-relaxed mb-4">
        {lead.description}
      </p>

      {/* Footer: Metadata & Matched Skills */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pt-3 border-t border-border/50 text-xs">
        {/* Matched Skill Chips */}
        <div className="flex items-center gap-1.5 flex-wrap">
          {visibleSkills.map((skill) => (
            <Chip key={skill} size="sm" matched>
              {skill}
            </Chip>
          ))}
          {remainingSkillsCount > 0 && (
            <span className="text-[11px] text-text-muted font-mono px-1">
              +{remainingSkillsCount} more
            </span>
          )}
        </div>

        {/* Location & Compensation Details */}
        <div className="flex items-center gap-3 text-text-muted shrink-0">
          {lead.salary_info && (
            <span className="flex items-center gap-1 font-mono text-text-secondary font-medium">
              <DollarSign className="w-3.5 h-3.5 text-accent" />
              {lead.salary_info}
            </span>
          )}
          {lead.location && !lead.is_remote && (
            <span className="flex items-center gap-1 truncate max-w-[120px]">
              <MapPin className="w-3.5 h-3.5" />
              {lead.location}
            </span>
          )}
          <span className="flex items-center gap-1">
            <Calendar className="w-3.5 h-3.5" />
            {formattedDate}
          </span>
          <ChevronRight className="w-4 h-4 text-text-muted group-hover:text-accent group-hover:translate-x-0.5 transition-all" />
        </div>
      </div>
    </div>
  )
}
