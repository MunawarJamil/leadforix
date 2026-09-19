import * as React from 'react'
import {
  Briefcase,
  Calendar,
  CheckCircle2,
  DollarSign,
  ExternalLink,
  MapPin,
  Send,
  Sparkles,
  X,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Chip } from '@/components/ui/chip'
import { ScoreGauge } from '@/components/widgets/score-gauge'
import { SourcePill } from '@/components/widgets/source-pill'
import type { Lead } from '../types/lead'

export interface LeadDetailDrawerProps {
  lead: Lead | null
  isOpen: boolean
  onClose: () => void
  onPrepareOutreach?: (lead: Lead) => void
}

export const LeadDetailDrawer: React.FC<LeadDetailDrawerProps> = ({
  lead,
  isOpen,
  onClose,
  onPrepareOutreach,
}) => {
  // Close drawer on Escape key
  React.useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) onClose()
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [isOpen, onClose])

  if (!isOpen || !lead) return null

  const formattedPostedDate = lead.posted_at
    ? new Date(lead.posted_at).toLocaleDateString(undefined, {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
      })
    : 'Unknown'

  const formattedDiscoveredDate = new Date(lead.discovered_at).toLocaleDateString(
    undefined,
    {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    }
  )

  return (
    <div className="fixed inset-0 z-50 flex justify-end">
      {/* Backdrop */}
      <div
        onClick={onClose}
        className="fixed inset-0 bg-black/60 backdrop-blur-xs transition-opacity animate-fade-in"
      />

      {/* Slide-Over Panel */}
      <div className="relative w-full max-w-2xl bg-surface/95 backdrop-blur-2xl border-l border-zinc-800/80 h-full shadow-2xl flex flex-col z-10 animate-slide-in overflow-hidden">
        {/* Top Accent Gradient Beam */}
        <div
          aria-hidden="true"
          className="pointer-events-none absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r from-transparent via-accent to-transparent opacity-80 z-20"
        />

        {/* Drawer Header */}
        <div className="p-6 border-b border-zinc-800/80 flex items-start justify-between gap-4 bg-surface/90 backdrop-blur-md sticky top-0 z-10">
          <div className="space-y-1.5 min-w-0">
            <div className="flex items-center gap-2 flex-wrap">
              <span className="text-xs uppercase font-mono tracking-wider text-accent font-bold">
                {lead.company_name}
              </span>
              <SourcePill source={lead.source} size="sm" />
              {lead.is_remote && (
                <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-medium border border-emerald-500/30 bg-emerald-500/10 text-emerald-400">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                  <span>Remote</span>
                </span>
              )}
            </div>
            <h2 className="text-xl sm:text-2xl font-bold text-text-primary font-display tracking-tight">
              {lead.title}
            </h2>
          </div>

          <button
            type="button"
            onClick={onClose}
            className="p-2 rounded-xl border border-zinc-800 bg-zinc-900/60 hover:bg-surface-hover text-text-muted hover:text-text-primary transition-colors shrink-0"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Drawer Scrollable Content */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {/* Match Score Intelligence Box */}
          <div className="relative overflow-hidden p-5 rounded-2xl border border-zinc-800/80 bg-zinc-900/40 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div className="absolute -top-px left-4 right-4 h-px bg-gradient-to-r from-transparent via-accent/30 to-transparent" />
            <div className="space-y-1">
              <span className="text-xs font-semibold text-accent flex items-center gap-1.5">
                <Sparkles className="w-3.5 h-3.5 text-accent animate-pulse" />
                <span>Algorithm Skill Alignment</span>
              </span>
              <p className="text-xs text-text-secondary leading-relaxed">
                Calculated by correlating requirement keywords with your target profile vector.
              </p>
            </div>
            <ScoreGauge score={lead.match_score} size="lg" />
          </div>

          {/* Matched Skills Overview */}
          {lead.matched_skills.length > 0 && (
            <div className="space-y-2.5">
              <h4 className="text-xs font-mono uppercase tracking-wider text-text-muted font-semibold">
                Detected Matching Skills ({lead.matched_skills.length})
              </h4>
              <div className="flex flex-wrap gap-1.5">
                {lead.matched_skills.map((skill) => (
                  <Chip
                    key={skill}
                    matched
                    size="default"
                    className="border-emerald-500/30 bg-emerald-950/30 text-emerald-400 font-mono text-xs px-3 py-1"
                  >
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 mr-1.5 inline" />
                    {skill}
                  </Chip>
                ))}
              </div>
            </div>
          )}

          {/* Metadata Grid */}
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3.5 p-4 sm:p-5 rounded-2xl border border-zinc-800/80 bg-zinc-900/30 text-xs">
            <div>
              <span className="text-text-muted block mb-1">Location</span>
              <span className="text-text-primary font-medium flex items-center gap-1.5">
                <MapPin className="w-3.5 h-3.5 text-text-muted" />
                {lead.is_remote ? 'Remote' : lead.location || 'Not Specified'}
              </span>
            </div>

            <div>
              <span className="text-text-muted block mb-1">Compensation</span>
              <span className="text-text-primary font-medium flex items-center gap-1 font-mono">
                <DollarSign className="w-3.5 h-3.5 text-accent" />
                {lead.salary_info || 'Undisclosed'}
              </span>
            </div>

            <div>
              <span className="text-text-muted block mb-1">Original Source</span>
              <span className="text-text-primary font-medium capitalize">
                {lead.source.replace('_', ' ')}
              </span>
            </div>

            <div>
              <span className="text-text-muted block mb-1">Posted On</span>
              <span className="text-text-primary font-medium flex items-center gap-1.5">
                <Calendar className="w-3.5 h-3.5 text-text-muted" />
                {formattedPostedDate}
              </span>
            </div>

            <div>
              <span className="text-text-muted block mb-1">Discovered</span>
              <span className="text-text-primary font-medium font-mono">
                {formattedDiscoveredDate}
              </span>
            </div>

            <div>
              <span className="text-text-muted block mb-1">Pipeline Status</span>
              <span className="text-accent font-semibold font-mono">
                {lead.status}
              </span>
            </div>
          </div>

          {/* Complete Job Description */}
          <div className="space-y-2.5">
            <h4 className="text-xs font-mono uppercase tracking-wider text-text-muted font-semibold flex items-center gap-1.5">
              <Briefcase className="w-3.5 h-3.5 text-accent" />
              <span>Full Opportunity Posting</span>
            </h4>
            <div className="p-5 rounded-2xl border border-zinc-800/80 bg-zinc-900/30 text-sm text-text-secondary leading-relaxed sm:leading-loose whitespace-pre-line font-sans select-text max-h-96 overflow-y-auto">
              {lead.description}
            </div>
          </div>
        </div>

        {/* Drawer Action Footer */}
        <div className="p-5 border-t border-zinc-800/80 bg-surface/90 backdrop-blur-md flex items-center justify-between gap-3 sticky bottom-0 z-10">
          <a
            href={lead.source_url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 px-4 py-2 rounded-xl border border-zinc-800 bg-zinc-900/60 hover:bg-surface-hover text-text-primary text-xs font-medium transition-colors"
          >
            <span>Open Source Post</span>
            <ExternalLink className="w-3.5 h-3.5 text-text-muted" />
          </a>

          <Button
            type="button"
            onClick={() => onPrepareOutreach?.(lead)}
            leftIcon={<Send className="w-3.5 h-3.5" />}
            size="default"
            className="rounded-xl shadow-lg shadow-accent/20"
          >
            Prepare AI Outreach
          </Button>
        </div>
      </div>
    </div>
  )
}
