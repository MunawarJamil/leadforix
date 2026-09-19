import * as React from 'react'
import {
  Building2,
  Check,
  ChevronDown,
  Clock,
  Globe,
  Laptop,
  RefreshCw,
  Search,
  SlidersHorizontal,
  X,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { SnakeBorder } from '@/components/ui/snake-border'
import { cn } from '@/lib/utils'
import type { FreshnessFilter, LeadFilterState, WorkplaceFilter } from '../types/lead'

export interface FilterToolbarProps {
  filters: LeadFilterState
  onFilterChange: (filters: LeadFilterState) => void
  onTriggerDiscovery?: () => void
  isDiscovering?: boolean
  totalCount: number
  filteredCount: number
  className?: string
}

const TYPEWRITER_PHRASES = [
  'company name...',
  'job title...',
  'your skills...',
]

const WORKPLACE_OPTIONS: {
  id: WorkplaceFilter
  label: string
  shortLabel: string
  icon: React.ComponentType<{ className?: string }>
  colorClass: string
}[] = [
  {
    id: 'ALL',
    label: 'All Workplaces',
    shortLabel: 'Apply Filter',
    icon: SlidersHorizontal,
    colorClass: 'text-text-secondary',
  },
  {
    id: 'REMOTE',
    label: 'Remote Only',
    shortLabel: 'Remote Only',
    icon: Globe,
    colorClass: 'text-emerald-400',
  },
  {
    id: 'HYBRID',
    label: 'Hybrid Only',
    shortLabel: 'Hybrid',
    icon: Laptop,
    colorClass: 'text-amber-400',
  },
  {
    id: 'ONSITE',
    label: 'Onsite Only',
    shortLabel: 'Onsite',
    icon: Building2,
    colorClass: 'text-cyan-400',
  },
]

const FRESHNESS_OPTIONS: {
  id: FreshnessFilter
  label: string
  shortLabel: string
}[] = [
  { id: 'ALL', label: 'All Time', shortLabel: 'All Time' },
  { id: '24H', label: 'Past 24 Hours', shortLabel: 'Past 24 hrs' },
  { id: '3D', label: 'Past 3 Days', shortLabel: 'Past 3 days' },
  { id: '1W', label: 'Past 1 Week', shortLabel: 'Past 1 week' },
  { id: '1M', label: 'Past 1 Month', shortLabel: 'Past 1 month' },
]

export const FilterToolbar: React.FC<FilterToolbarProps> = ({
  filters,
  onFilterChange,
  onTriggerDiscovery,
  isDiscovering = false,
  className,
}) => {
  const [isFilterMenuOpen, setIsFilterMenuOpen] = React.useState(false)
  const [isFreshnessMenuOpen, setIsFreshnessMenuOpen] = React.useState(false)
  const [isInputFocused, setIsInputFocused] = React.useState(false)

  const dropdownRef = React.useRef<HTMLDivElement>(null)
  const freshnessRef = React.useRef<HTMLDivElement>(null)

  // Character-by-character typewriter animation
  const [phraseIndex, setPhraseIndex] = React.useState(0)
  const [animatedSuffix, setAnimatedSuffix] = React.useState('')
  const [isDeleting, setIsDeleting] = React.useState(false)

  React.useEffect(() => {
    // Pause animation when user clicks/focuses inside the search bar
    if (isInputFocused) return

    const currentPhrase = TYPEWRITER_PHRASES[phraseIndex]

    if (!isDeleting) {
      if (animatedSuffix.length < currentPhrase.length) {
        const timeout = setTimeout(() => {
          setAnimatedSuffix(currentPhrase.slice(0, animatedSuffix.length + 1))
        }, 85)
        return () => clearTimeout(timeout)
      } else {
        const timeout = setTimeout(() => {
          setIsDeleting(true)
        }, 1700)
        return () => clearTimeout(timeout)
      }
    } else {
      if (animatedSuffix.length > 0) {
        const timeout = setTimeout(() => {
          setAnimatedSuffix(currentPhrase.slice(0, animatedSuffix.length - 1))
        }, 40)
        return () => clearTimeout(timeout)
      } else {
        const timeout = setTimeout(() => {
          setIsDeleting(false)
          setPhraseIndex((prev) => (prev + 1) % TYPEWRITER_PHRASES.length)
        }, 300)
        return () => clearTimeout(timeout)
      }
    }
  }, [animatedSuffix, isDeleting, phraseIndex, isInputFocused])

  // Close dropdowns on outside click
  React.useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setIsFilterMenuOpen(false)
      }
      if (freshnessRef.current && !freshnessRef.current.contains(e.target as Node)) {
        setIsFreshnessMenuOpen(false)
      }
    }
    if (isFilterMenuOpen || isFreshnessMenuOpen) {
      document.addEventListener('mousedown', handleClickOutside)
    }
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [isFilterMenuOpen, isFreshnessMenuOpen])

  const currentWorkplace: WorkplaceFilter =
    filters.workplaceType || (filters.remoteOnly ? 'REMOTE' : 'ALL')

  const selectedWorkplace =
    WORKPLACE_OPTIONS.find((opt) => opt.id === currentWorkplace) || WORKPLACE_OPTIONS[0]

  const currentFreshness: FreshnessFilter = filters.freshness || 'ALL'
  const selectedFreshness =
    FRESHNESS_OPTIONS.find((opt) => opt.id === currentFreshness) || FRESHNESS_OPTIONS[0]

  const handleSelectWorkplace = (id: WorkplaceFilter) => {
    onFilterChange({
      ...filters,
      workplaceType: id,
      remoteOnly: id === 'REMOTE',
    })
    setIsFilterMenuOpen(false)
  }

  const handleSelectFreshness = (id: FreshnessFilter) => {
    onFilterChange({
      ...filters,
      freshness: id,
    })
    setIsFreshnessMenuOpen(false)
  }

  const SelectedWorkplaceIcon = selectedWorkplace.icon

  return (
    <div
      className={cn(
        'relative z-30 overflow-visible rounded-2xl border border-zinc-800/80 bg-surface/90 backdrop-blur-xl p-3 sm:p-4 shadow-xl shadow-black/20 w-full',
        className
      )}
    >
      <div className="relative z-30 flex flex-col md:flex-row items-stretch md:items-center gap-2.5 sm:gap-3">
        {/* Row 1 / Left Section: Search Input + Tight SnakeBorder Fetch Button */}
        <div className="flex flex-1 items-center gap-2 sm:gap-2.5 min-w-0">
          {/* Search Input Container with Typewriter Animated Text */}
          <div className="relative flex-1 group min-w-0">
            <Input
              placeholder=""
              value={filters.searchQuery}
              onFocus={() => setIsInputFocused(true)}
              onBlur={() => setIsInputFocused(false)}
              onChange={(e) => onFilterChange({ ...filters, searchQuery: e.target.value })}
              leftIcon={<Search className="w-4 h-4 text-text-muted group-focus-within:text-accent transition-colors" />}
              className="pr-9 bg-zinc-900/60 border-zinc-800 focus:border-accent/60 focus:ring-accent/20 rounded-xl h-10 text-xs sm:text-sm w-full"
            />

            {/* Typewriter Dynamic Placeholder Overlay (Hidden when focused or searching) */}
            {!filters.searchQuery && !isInputFocused && (
              <div className="pointer-events-none absolute left-9 sm:left-10 top-1/2 -translate-y-1/2 text-xs sm:text-sm text-text-muted flex items-center gap-1.5 select-none overflow-hidden max-w-[calc(100%-3.5rem)] animate-fade-in">
                <span className="shrink-0 text-text-secondary">Search leads by</span>
                <span className="text-accent font-medium inline-flex items-center min-w-0 truncate">
                  <span className="truncate">{animatedSuffix}</span>
                  <span className="animate-pulse text-accent ml-0.5 font-bold shrink-0">|</span>
                </span>
              </div>
            )}

            {filters.searchQuery && (
              <button
                type="button"
                onClick={() => onFilterChange({ ...filters, searchQuery: '' })}
                className="absolute right-2.5 top-1/2 -translate-y-1/2 text-text-muted hover:text-text-primary p-1 rounded-md hover:bg-surface-hover transition-colors"
                title="Clear search"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            )}
          </div>

          {/* 2. Fetch Fresh Leads Button with tightly fitted SnakeBorder */}
          {onTriggerDiscovery && (
            <div className="group/fresh relative inline-flex items-center justify-center rounded-xl shrink-0">
              <SnakeBorder
                className="z-20 pointer-events-none opacity-60 transition-opacity duration-300 group-hover/fresh:opacity-0"
                colorFrom="#6366F1"
                colorTo="#A78BFA"
                duration={7}
                size={20}
                strokeWidth={1}
                rx={12}
              />
              <Button
                type="button"
                variant="outline"
                size="default"
                onClick={onTriggerDiscovery}
                isLoading={isDiscovering}
                leftIcon={<RefreshCw className={cn('w-3.5 h-3.5', isDiscovering && 'animate-spin')} />}
                className="relative z-10 h-10 px-3 sm:px-4 rounded-xl border-zinc-800/80 bg-zinc-900/90 hover:bg-surface-hover hover:border-accent/40 text-xs font-medium backdrop-blur-sm whitespace-nowrap shrink-0"
              >
                <span className="hidden sm:inline">Fetch Fresh Leads</span>
                <span className="inline sm:hidden">Fetch</span>
              </Button>
            </div>
          )}
        </div>

        {/* Filter Controls: Workplace & Freshness Dropdowns */}
        <div className="flex items-center gap-2 sm:gap-2.5 justify-between md:justify-end shrink-0 relative z-40 w-full md:w-auto">
          {/* Apply Workplace Filter Dropdown */}
          <div className="relative flex-1 md:flex-initial z-50" ref={dropdownRef}>
            <button
              type="button"
              onClick={() => {
                setIsFilterMenuOpen((prev) => !prev)
                setIsFreshnessMenuOpen(false)
              }}
              className={cn(
                'w-full md:w-auto inline-flex items-center justify-between md:justify-start gap-2 px-3 sm:px-3.5 h-10 rounded-xl text-xs font-medium border transition-all select-none',
                currentWorkplace !== 'ALL'
                  ? 'border-accent/50 bg-accent/10 text-text-primary shadow-xs ring-1 ring-accent/30'
                  : 'border-zinc-800 bg-zinc-900/60 hover:bg-surface-hover text-text-secondary hover:text-text-primary hover:border-zinc-700'
              )}
            >
              <div className="flex items-center gap-1.5 truncate">
                <SelectedWorkplaceIcon className={cn('w-3.5 h-3.5 shrink-0', selectedWorkplace.colorClass)} />
                <span className="truncate">{currentWorkplace === 'ALL' ? 'Apply Filter' : selectedWorkplace.label}</span>
              </div>
              <ChevronDown className={cn('w-3.5 h-3.5 text-text-muted transition-transform duration-200 shrink-0', isFilterMenuOpen && 'rotate-180')} />
            </button>

            {/* Workplace Popover */}
            {isFilterMenuOpen && (
              <div className="absolute left-0 md:left-auto md:right-0 top-full mt-2 w-full md:w-52 rounded-2xl border border-zinc-800 bg-surface/95 backdrop-blur-2xl shadow-2xl shadow-black/90 p-1.5 z-50 animate-fade-in">
                {WORKPLACE_OPTIONS.map((opt) => {
                  const isSelected = currentWorkplace === opt.id
                  const OptIcon = opt.icon
                  return (
                    <button
                      key={opt.id}
                      type="button"
                      onClick={() => handleSelectWorkplace(opt.id)}
                      className={cn(
                        'w-full flex items-center justify-between px-3 py-2 rounded-xl text-xs font-medium transition-colors text-left',
                        isSelected
                          ? 'bg-zinc-800/90 text-text-primary font-semibold'
                          : 'hover:bg-zinc-800/50 text-text-secondary hover:text-text-primary'
                      )}
                    >
                      <div className="flex items-center gap-2">
                        <OptIcon className={cn('w-3.5 h-3.5', opt.colorClass)} />
                        <span>{opt.label}</span>
                      </div>
                      {isSelected && <Check className="w-3.5 h-3.5 text-accent" />}
                    </button>
                  )
                })}
              </div>
            )}
          </div>

          {/* Freshness Date Range Dropdown */}
          <div className="relative flex-1 md:flex-initial z-50" ref={freshnessRef}>
            <button
              type="button"
              onClick={() => {
                setIsFreshnessMenuOpen((prev) => !prev)
                setIsFilterMenuOpen(false)
              }}
              className={cn(
                'w-full md:w-auto inline-flex items-center justify-between md:justify-start gap-2 px-3 sm:px-3.5 h-10 rounded-xl text-xs font-medium border transition-all select-none',
                currentFreshness !== 'ALL'
                  ? 'border-accent/50 bg-accent/10 text-text-primary shadow-xs ring-1 ring-accent/30'
                  : 'border-zinc-800 bg-zinc-900/60 hover:bg-surface-hover text-text-secondary hover:text-text-primary hover:border-zinc-700'
              )}
            >
              <div className="flex items-center gap-1.5 truncate">
                <Clock className={cn('w-3.5 h-3.5 shrink-0', currentFreshness !== 'ALL' ? 'text-accent' : 'text-text-muted')} />
                <span className="truncate">{currentFreshness === 'ALL' ? 'Freshness' : selectedFreshness.shortLabel}</span>
              </div>
              <ChevronDown className={cn('w-3.5 h-3.5 text-text-muted transition-transform duration-200 shrink-0', isFreshnessMenuOpen && 'rotate-180')} />
            </button>

            {/* Freshness Popover */}
            {isFreshnessMenuOpen && (
              <div className="absolute right-0 top-full mt-2 w-full md:w-48 rounded-2xl border border-zinc-800 bg-surface/95 backdrop-blur-2xl shadow-2xl shadow-black/90 p-1.5 z-50 animate-fade-in">
                {FRESHNESS_OPTIONS.map((opt) => {
                  const isSelected = currentFreshness === opt.id
                  return (
                    <button
                      key={opt.id}
                      type="button"
                      onClick={() => handleSelectFreshness(opt.id)}
                      className={cn(
                        'w-full flex items-center justify-between px-3 py-2 rounded-xl text-xs font-medium transition-colors text-left',
                        isSelected
                          ? 'bg-zinc-800/90 text-text-primary font-semibold'
                          : 'hover:bg-zinc-800/50 text-text-secondary hover:text-text-primary'
                      )}
                    >
                      <span>{opt.label}</span>
                      {isSelected && <Check className="w-3.5 h-3.5 text-accent" />}
                    </button>
                  )
                })}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
