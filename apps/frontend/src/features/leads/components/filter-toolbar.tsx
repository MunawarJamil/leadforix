import * as React from 'react'
import { Filter, RefreshCw, Search, SlidersHorizontal, X } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { cn } from '@/lib/utils'
import type { LeadFilterState, LeadSource } from '../types/lead'

export interface FilterToolbarProps {
  filters: LeadFilterState
  onFilterChange: (filters: LeadFilterState) => void
  onTriggerDiscovery?: () => void
  isDiscovering?: boolean
  totalCount: number
  filteredCount: number
  className?: string
}

const SOURCES: { id: 'ALL' | LeadSource; label: string }[] = [
  { id: 'ALL', label: 'All Sources' },
  { id: 'hacker_news', label: 'Hacker News' },
  { id: 'remotive', label: 'Remotive' },
  { id: 'arbeitnow', label: 'Arbeitnow' },
]

const SCORE_THRESHOLDS: { label: string; minScore: number }[] = [
  { label: 'All Scores', minScore: 0 },
  { label: '50%+ Potential', minScore: 50 },
  { label: '80%+ High Match', minScore: 80 },
]

export const FilterToolbar: React.FC<FilterToolbarProps> = ({
  filters,
  onFilterChange,
  onTriggerDiscovery,
  isDiscovering = false,
  totalCount,
  filteredCount,
  className,
}) => {
  return (
    <div className={cn('space-y-4 bg-surface p-4 rounded-xl border border-border', className)}>
      {/* Top Bar: Search + Discovery Trigger */}
      <div className="flex flex-col sm:flex-row gap-3 items-stretch sm:items-center justify-between">
        <div className="relative flex-1">
          <Input
            placeholder="Search by company, job title, or required skill (e.g. Python, Stripe)..."
            value={filters.searchQuery}
            onChange={(e) => onFilterChange({ ...filters, searchQuery: e.target.value })}
            leftIcon={<Search className="w-4 h-4 text-text-muted" />}
            className="pr-8"
          />
          {filters.searchQuery && (
            <button
              type="button"
              onClick={() => onFilterChange({ ...filters, searchQuery: '' })}
              className="absolute right-2.5 top-1/2 -translate-y-1/2 text-text-muted hover:text-text-primary p-1"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          )}
        </div>

        {onTriggerDiscovery && (
          <Button
            type="button"
            variant="outline"
            size="default"
            onClick={onTriggerDiscovery}
            isLoading={isDiscovering}
            leftIcon={<RefreshCw className={cn('w-3.5 h-3.5', isDiscovering && 'animate-spin')} />}
            className="shrink-0"
          >
            Fetch Fresh Leads
          </Button>
        )}
      </div>

      {/* Bottom Filter Controls */}
      <div className="flex flex-wrap items-center justify-between gap-3 pt-2 border-t border-border/50 text-xs">
        {/* Source Filter Pills */}
        <div className="flex items-center gap-1.5 flex-wrap">
          <span className="text-text-muted font-medium mr-1 flex items-center gap-1">
            <Filter className="w-3 h-3 text-accent" /> Source:
          </span>
          {SOURCES.map((src) => {
            const isActive = filters.source === src.id
            return (
              <button
                key={src.id}
                type="button"
                onClick={() => onFilterChange({ ...filters, source: src.id })}
                className={cn(
                  'px-2.5 py-1 rounded-md font-medium transition-colors',
                  isActive
                    ? 'bg-accent text-white shadow-xs'
                    : 'bg-background hover:bg-surface-hover text-text-secondary hover:text-text-primary border border-border'
                )}
              >
                {src.label}
              </button>
            )
          })}
        </div>

        {/* Score Threshold & Remote-Only Toggle */}
        <div className="flex items-center gap-4 flex-wrap">
          {/* Score Threshold */}
          <div className="flex items-center gap-1.5">
            <SlidersHorizontal className="w-3 h-3 text-text-muted" />
            <select
              value={filters.minScore}
              onChange={(e) =>
                onFilterChange({ ...filters, minScore: Number(e.target.value) })
              }
              className="bg-background border border-border rounded-md px-2 py-1 text-xs text-text-primary focus:outline-none focus:border-accent"
            >
              {SCORE_THRESHOLDS.map((thresh) => (
                <option key={thresh.minScore} value={thresh.minScore}>
                  {thresh.label}
                </option>
              ))}
            </select>
          </div>

          {/* Remote Only Toggle */}
          <label className="inline-flex items-center gap-2 cursor-pointer select-none">
            <input
              type="checkbox"
              checked={filters.remoteOnly}
              onChange={(e) =>
                onFilterChange({ ...filters, remoteOnly: e.target.checked })
              }
              className="rounded border-border bg-background text-accent focus:ring-accent/20 h-3.5 w-3.5"
            />
            <span className="text-text-secondary">Remote Only</span>
          </label>

          {/* Count Badge */}
          <span className="text-text-muted font-mono">
            Showing <strong className="text-text-primary">{filteredCount}</strong> of {totalCount}
          </span>
        </div>
      </div>
    </div>
  )
}
