import * as React from 'react'
import { Calendar, DollarSign, MapPin } from 'lucide-react'
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
        'group relative overflow-hidden rounded-2xl border transition-all duration-300 cursor-pointer p-5 sm:p-6 shadow-xl shadow-black/20 w-full',
        isSelected
          ? 'border-accent/70 bg-surface/95 shadow-accent/10 ring-1 ring-accent/30'
          : 'border-zinc-800/80 bg-surface/90 hover:border-zinc-700/90 hover:bg-surface hover:shadow-2xl hover:shadow-black/40',
        className
      )}
    >
      {/* Ambient Bottom Accent Glow Beam (Visible without hover) */}
      <div
        aria-hidden="true"
        className={cn(
          'pointer-events-none absolute bottom-0 left-0 right-0 h-[2px] bg-gradient-to-r from-transparent via-accent to-transparent transition-opacity duration-300',
          isSelected ? 'opacity-100' : 'opacity-70 group-hover:opacity-100'
        )}
      />

      {/* Selected Left Edge Indicator */}
      {isSelected && (
        <div
          aria-hidden="true"
          className="absolute left-0 top-0 bottom-0 w-[3px] bg-gradient-to-b from-accent via-accent to-accent-alt"
        />
      )}

      {/* Header: Company, Source Pill, Remote Beacon & Score Gauge + Detail Arrow */}
      <div className="flex items-start justify-between gap-3 sm:gap-4 mb-4 sm:mb-4.5">
        <div className="flex items-center gap-2 sm:gap-2.5 flex-wrap min-w-0 flex-1">
          <span className="font-bold text-accent text-sm sm:text-base tracking-tight font-sans">
            {lead.company_name}
          </span>
          <SourcePill source={lead.source} size="sm" />
          {lead.is_remote && (
            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-medium border border-emerald-500/30 bg-emerald-500/10 text-emerald-400 select-none shrink-0">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
              <span>Remote</span>
            </span>
          )}
        </div>

        {/* Top-Right: Clean Score Gauge */}
        <ScoreGauge score={lead.match_score} size="sm" showLabel={false} className="shrink-0" />
      </div>

      {/* Role Title with Editorial High-Contrast Styling (White title with serif display font) */}
      <h3 className="text-base sm:text-lg font-bold text-text-primary font-display tracking-tight group-hover:text-white transition-colors duration-200 line-clamp-2 leading-snug sm:leading-normal mb-3 sm:mb-3.5 break-words">
        {lead.title}
      </h3>

      {/* Brief Description Snippet with Enhanced Line Height */}
      <p className="text-xs sm:text-sm text-text-secondary line-clamp-2 leading-relaxed sm:leading-loose mb-5 sm:mb-5.5 font-sans">
        {lead.description}
      </p>

      {/* Footer: Matched Skill Chips & Metadata */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3.5 pt-4.5 sm:pt-5 border-t border-zinc-800/80 text-xs">
        {/* Matched Skill Chips */}
        <div className="flex items-center gap-1.5 flex-wrap">
          {visibleSkills.map((skill) => (
            <Chip
              key={skill}
              size="sm"
              matched
              className="border-emerald-500/30 bg-emerald-950/30 text-emerald-400 font-mono text-[11px] px-2.5 py-0.5"
            >
              {skill}
            </Chip>
          ))}
          {remainingSkillsCount > 0 && (
            <span className="text-[11px] text-text-muted font-mono px-2 py-0.5 rounded-md bg-zinc-900 border border-zinc-800">
              +{remainingSkillsCount} more
            </span>
          )}
        </div>

        {/* Location, Compensation & Hover Reveal "View Details →" */}
        <div className="flex items-center gap-3 text-text-muted shrink-0">
          {lead.salary_info && (
            <span className="flex items-center gap-1 font-mono text-xs text-text-primary font-medium px-2.5 py-1 rounded-lg bg-zinc-900/60 border border-zinc-800/60">
              <DollarSign className="w-3.5 h-3.5 text-accent shrink-0" />
              <span>{lead.salary_info}</span>
            </span>
          )}
          {lead.location && !lead.is_remote && (
            <span className="flex items-center gap-1 text-xs text-text-secondary truncate max-w-[140px]">
              <MapPin className="w-3.5 h-3.5 text-text-muted shrink-0" />
              <span className="truncate">{lead.location}</span>
            </span>
          )}
          <span className="flex items-center gap-1 text-xs text-text-muted">
            <Calendar className="w-3.5 h-3.5 text-text-muted shrink-0" />
            <span>{formattedDate}</span>
          </span>

          {/* Hover Reveal: View Details → */}
          <span className="inline-flex items-center gap-1 text-xs font-mono font-medium text-accent opacity-0 group-hover:opacity-100 transition-all duration-200 transform translate-x-1 group-hover:translate-x-0">
            <span>View Details</span>
            <span className="transition-transform duration-200 group-hover:translate-x-0.5">&rarr;</span>
          </span>
        </div>
      </div>
    </div>
  )
}
