import * as React from 'react'
import { ChevronLeft, ChevronRight, Sparkles } from 'lucide-react'
import { EmptyState } from '@/components/widgets/empty-state'
import { cn } from '@/lib/utils'
import type { Lead, LeadFilterState } from '../types/lead'
import { FilterToolbar } from './filter-toolbar'
import { LeadCard } from './lead-card'
import { LeadDetailDrawer } from './lead-detail-drawer'

// High-intent seed data representing our three live discovery sources
const INITIAL_SEED_LEADS: Lead[] = [
  {
    id: 'lead-001',
    company_name: 'Supabase',
    title: 'Senior Backend Engineer (Python & PostgreSQL)',
    description:
      'Supabase is an open source Firebase alternative. We are seeking a Senior Backend Engineer to expand our internal telemetry, real-time sync engines, and async task pipelines. You will design scalable data pipelines in Python and optimize high-throughput PostgreSQL queries.',
    source: 'hacker_news',
    source_url: 'https://news.ycombinator.com/item?id=38000001',
    source_id: 'hn-38000001',
    location: 'Remote (Global)',
    is_remote: true,
    salary_info: '$150,000 - $190,000',
    match_score: 94,
    matched_skills: ['Python', 'PostgreSQL', 'Docker', 'FastAPI'],
    status: 'QUALIFIED',
    posted_at: new Date(Date.now() - 2 * 3600 * 1000).toISOString(),
    discovered_at: new Date().toISOString(),
  },
  {
    id: 'lead-002',
    company_name: 'Pinecone Systems',
    title: 'AI Systems Engineer (LangChain & Vector DB)',
    description:
      'Join Pinecone to architect next-generation vector infrastructure for production LLM systems. Working closely with RAG workflows, LangChain integrations, and Kubernetes clusters to power agentic search architectures for enterprise customers.',
    source: 'remotive',
    source_url: 'https://remotive.com/remote-jobs/software-dev/ai-systems-engineer',
    source_id: 'remotive-98124',
    location: 'Remote (US & Canada)',
    is_remote: true,
    salary_info: '$165,000 - $210,000',
    match_score: 88,
    matched_skills: ['LangChain', 'Python', 'Docker', 'AWS'],
    status: 'QUALIFIED',
    posted_at: new Date(Date.now() - 5 * 3600 * 1000).toISOString(),
    discovered_at: new Date().toISOString(),
  },
  {
    id: 'lead-003',
    company_name: 'Delivery Hero',
    title: 'Fullstack Platform Engineer (TypeScript & React)',
    description:
      'Delivery Hero is building the future of quick commerce across 70+ countries. We are looking for an experienced Fullstack Engineer with strong proficiency in React 19, TypeScript, state management, and modern distributed microservices to craft customer-facing merchant dashboards.',
    source: 'arbeitnow',
    source_url: 'https://www.arbeitnow.com/jobs/companies/delivery-hero/fullstack-platform-engineer',
    source_id: 'arbeitnow-44910',
    location: 'Berlin, Germany',
    is_remote: true,
    salary_info: '€85,000 - €105,000',
    match_score: 82,
    matched_skills: ['TypeScript', 'React', 'TailwindCSS'],
    status: 'QUALIFIED',
    posted_at: new Date(Date.now() - 14 * 3600 * 1000).toISOString(),
    discovered_at: new Date().toISOString(),
  },
  {
    id: 'lead-004',
    company_name: 'Vercel',
    title: 'Frontend Infrastructure Specialist',
    description:
      'Help build developer experience platforms for modern web frameworks. Deep expertise required in TypeScript compiler APIs, bundle optimization, and high-performance React component libraries.',
    source: 'hacker_news',
    source_url: 'https://news.ycombinator.com/item?id=38000045',
    source_id: 'hn-38000045',
    location: 'Remote',
    is_remote: true,
    salary_info: '$140,000 - $185,000',
    match_score: 76,
    matched_skills: ['TypeScript', 'React', 'Next.js'],
    status: 'QUALIFIED',
    posted_at: new Date(Date.now() - 24 * 3600 * 1000).toISOString(),
    discovered_at: new Date().toISOString(),
  },
  {
    id: 'lead-005',
    company_name: 'Klarna',
    title: 'Data & Distributed Systems Engineer',
    description:
      'We are expanding our payment fraud detection pipeline. Requires experience with Kafka streaming, distributed cache layers in Redis, and asynchronous microservices in Go or Python.',
    source: 'arbeitnow',
    source_url: 'https://www.arbeitnow.com/jobs/companies/klarna/distributed-systems-engineer',
    source_id: 'arbeitnow-55129',
    location: 'Stockholm, Sweden',
    is_remote: false,
    salary_info: '€90,000 - €115,000',
    match_score: 58,
    matched_skills: ['Python', 'Redis', 'Docker'],
    status: 'NEW',
    posted_at: new Date(Date.now() - 48 * 3600 * 1000).toISOString(),
    discovered_at: new Date().toISOString(),
  },
  {
    id: 'lead-006',
    company_name: 'Linear',
    title: 'Staff Fullstack Product Engineer (React & TypeScript)',
    description:
      'Building the next generation of project tracking and engineering issue coordination. Looking for deep craft in React rendering performance, WebSocket synchronization, and intuitive UX design.',
    source: 'remotive',
    source_url: 'https://remotive.com/remote-jobs/linear-staff-engineer',
    source_id: 'remotive-77182',
    location: 'Remote (Worldwide)',
    is_remote: true,
    salary_info: '$170,000 - $220,000',
    match_score: 86,
    matched_skills: ['React', 'TypeScript', 'Docker', 'FastAPI'],
    status: 'QUALIFIED',
    posted_at: new Date(Date.now() - 12 * 3600 * 1000).toISOString(),
    discovered_at: new Date().toISOString(),
  },
  {
    id: 'lead-007',
    company_name: 'Vercel',
    title: 'Edge Infrastructure & Telemetry Engineer',
    description:
      'Scale our global edge compute network. Seeking engineers proficient in distributed tracing, high-throughput caching with Redis, and zero-downtime containerized microservices.',
    source: 'hacker_news',
    source_url: 'https://news.ycombinator.com/item?id=38000007',
    source_id: 'hn-38000007',
    location: 'Remote (US & EMEA)',
    is_remote: true,
    salary_info: '$180,000 - $230,000',
    match_score: 91,
    matched_skills: ['Python', 'Docker', 'Redis', 'PostgreSQL'],
    status: 'QUALIFIED',
    posted_at: new Date(Date.now() - 8 * 3600 * 1000).toISOString(),
    discovered_at: new Date().toISOString(),
  },
  {
    id: 'lead-008',
    company_name: 'Datadog',
    title: 'Distributed Systems & Observability Specialist',
    description:
      'Develop real-time ingestion pipelines processing millions of telemetry events per second. Deep profiling in Python, async processing, and multi-region database replication.',
    source: 'arbeitnow',
    source_url: 'https://www.arbeitnow.com/jobs/datadog-systems',
    source_id: 'arbeitnow-99411',
    location: 'Paris, France (Hybrid)',
    is_remote: false,
    salary_info: '€95,000 - €125,000',
    match_score: 74,
    matched_skills: ['Python', 'Docker', 'PostgreSQL'],
    status: 'NEW',
    posted_at: new Date(Date.now() - 36 * 3600 * 1000).toISOString(),
    discovered_at: new Date().toISOString(),
  },
  {
    id: 'lead-009',
    company_name: 'Stripe',
    title: 'API Platform & Developer Experience Engineer',
    description:
      'Architect robust developer tools and high-reliability payment webhook dispatchers. Heavy emphasis on rate limiting, idempotency keys, and resilient asynchronous worker queues.',
    source: 'hacker_news',
    source_url: 'https://news.ycombinator.com/item?id=38000009',
    source_id: 'hn-38000009',
    location: 'Remote (Global)',
    is_remote: true,
    salary_info: '$190,000 - $240,000',
    match_score: 84,
    matched_skills: ['Python', 'FastAPI', 'PostgreSQL', 'Docker'],
    status: 'QUALIFIED',
    posted_at: new Date(Date.now() - 16 * 3600 * 1000).toISOString(),
    discovered_at: new Date().toISOString(),
  },
  {
    id: 'lead-010',
    company_name: 'Qdrant',
    title: 'Vector Engine Core & Integration Engineer',
    description:
      'Craft high-performance embeddings retrieval and approximate nearest-neighbor indexing layers for LLM and RAG developers worldwide. Open source contributions welcome.',
    source: 'remotive',
    source_url: 'https://remotive.com/remote-jobs/qdrant-engine',
    source_id: 'remotive-44109',
    location: 'Berlin, Germany',
    is_remote: true,
    salary_info: '€110,000 - €140,000',
    match_score: 95,
    matched_skills: ['LangChain', 'Python', 'Docker', 'FastAPI'],
    status: 'QUALIFIED',
    posted_at: new Date(Date.now() - 4 * 3600 * 1000).toISOString(),
    discovered_at: new Date().toISOString(),
  },
]

export interface LeadFeedProps {
  initialLeads?: Lead[]
  onPrepareOutreach?: (lead: Lead) => void
  className?: string
}

export const LeadFeed: React.FC<LeadFeedProps> = ({
  initialLeads = INITIAL_SEED_LEADS,
  onPrepareOutreach,
  className,
}) => {
  const [leads] = React.useState<Lead[]>(initialLeads)
  const [selectedLead, setSelectedLead] = React.useState<Lead | null>(null)
  const [isDrawerOpen, setIsDrawerOpen] = React.useState(false)
  const [isDiscovering, setIsDiscovering] = React.useState(false)
  const [currentTime, setCurrentTime] = React.useState(() => Date.now())

  // Pagination state (5 leads per page)
  const [currentPage, setCurrentPage] = React.useState(1)
  const pageSize = 5

  const [filters, setFilters] = React.useState<LeadFilterState>({
    searchQuery: '',
    source: 'ALL',
    minScore: 0,
    remoteOnly: false,
    workplaceType: 'ALL',
    freshness: 'ALL',
    status: 'ALL',
  })

  // Handle filter updates & reset pagination directly during event dispatch (no cascading render effect)
  const handleFilterChange = (newFilters: LeadFilterState) => {
    setFilters(newFilters)
    setCurrentPage(1)
  }

  // Multi-criteria client-side filtering
  const filteredLeads = React.useMemo(() => {
    return leads.filter((lead) => {
      // 1. Text Search query (matches title, company, or matched skills)
      if (filters.searchQuery.trim()) {
        const query = filters.searchQuery.toLowerCase()
        const matchesCompany = lead.company_name.toLowerCase().includes(query)
        const matchesTitle = lead.title.toLowerCase().includes(query)
        const matchesSkill = lead.matched_skills.some((s) =>
          s.toLowerCase().includes(query)
        )
        const matchesDesc = lead.description.toLowerCase().includes(query)

        if (!matchesCompany && !matchesTitle && !matchesSkill && !matchesDesc) {
          return false
        }
      }

      // 2. Source filter
      if (filters.source !== 'ALL' && lead.source !== filters.source) {
        return false
      }

      // 3. Minimum match score
      if (lead.match_score < filters.minScore) {
        return false
      }

      // 4. Workplace filter (Remote, Hybrid, Onsite, All)
      if (filters.workplaceType === 'REMOTE' || (filters.remoteOnly && !filters.workplaceType)) {
        if (!lead.is_remote) return false
      } else if (filters.workplaceType === 'ONSITE') {
        if (lead.is_remote) return false
      } else if (filters.workplaceType === 'HYBRID') {
        const text = `${lead.location || ''} ${lead.description || ''}`.toLowerCase()
        if (!text.includes('hybrid')) return false
      }

      // 5. Freshness / Posted Date filter
      if (filters.freshness && filters.freshness !== 'ALL' && lead.posted_at) {
        const leadTime = new Date(lead.posted_at).getTime()
        const diffHours = (currentTime - leadTime) / (1000 * 3600)

        if (filters.freshness === '24H' && diffHours > 24) return false
        if (filters.freshness === '3D' && diffHours > 72) return false
        if (filters.freshness === '1W' && diffHours > 168) return false
        if (filters.freshness === '1M' && diffHours > 720) return false
      }

      // 6. Status filter
      if (filters.status !== 'ALL' && lead.status !== filters.status) {
        return false
      }

      return true
    })
  }, [leads, filters, currentTime])

  // Paginated leads slice for current page
  const totalPages = Math.max(1, Math.ceil(filteredLeads.length / pageSize))
  const safeCurrentPage = Math.min(currentPage, totalPages)
  const paginatedLeads = React.useMemo(() => {
    const start = (safeCurrentPage - 1) * pageSize
    return filteredLeads.slice(start, start + pageSize)
  }, [filteredLeads, safeCurrentPage, pageSize])

  const handleSelectLead = (lead: Lead) => {
    setSelectedLead(lead)
    setIsDrawerOpen(true)
  }

  const handleCloseDrawer = () => {
    setIsDrawerOpen(false)
    setTimeout(() => setSelectedLead(null), 200)
  }

  const handleTriggerDiscovery = () => {
    setIsDiscovering(true)
    setTimeout(() => {
      setIsDiscovering(false)
      setCurrentTime(Date.now())
    }, 2000)
  }

  const handleResetFilters = () => {
    setFilters({
      searchQuery: '',
      source: 'ALL',
      minScore: 0,
      remoteOnly: false,
      workplaceType: 'ALL',
      freshness: 'ALL',
      status: 'ALL',
    })
    setCurrentPage(1)
  }

  // Real-time KPI summary calculations
  const stats = React.useMemo(() => {
    const total = leads.length
    const highMatches = leads.filter((l) => l.match_score >= 80).length
    const remoteCount = leads.filter((l) => l.is_remote).length
    const remotePercentage = total > 0 ? Math.round((remoteCount / total) * 100) : 0
    return {
      total,
      highMatches,
      remoteCount,
      remotePercentage,
      sourcesCount: 3,
    }
  }, [leads])

  return (
    <div className={cn('space-y-7 sm:space-y-8 max-w-4xl mx-auto w-full min-w-0', className)}>
      {/* Opportunities Identity Header Banner (Consistent with Profile Name Section) */}
      <div className="relative overflow-hidden rounded-2xl border border-zinc-800/80 bg-surface/90 backdrop-blur-xl p-5 sm:p-7 shadow-xl shadow-black/30 w-full">
        <div
          aria-hidden="true"
          className="pointer-events-none absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r from-transparent via-accent to-transparent opacity-80"
        />
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-5">
          {/* Feed Info */}
          <div className="flex items-center gap-4 sm:gap-5 min-w-0">
            {/* Feed Avatar Badge */}
            <div className="relative flex h-14 w-14 sm:h-18 sm:w-18 shrink-0 items-center justify-center rounded-2xl bg-gradient-to-br from-accent/25 via-accent/10 to-surface border border-accent/40 shadow-lg shadow-accent/20">
              <span className="text-lg sm:text-xl font-bold font-mono tracking-tight text-accent">
                MO
              </span>
              <span className="absolute -bottom-1 -right-1 flex h-3.5 w-3.5 sm:h-4 sm:w-4">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-30" />
                <span className="relative inline-flex rounded-full h-3.5 w-3.5 sm:h-4 sm:w-4 bg-emerald-500/80 border-2 border-surface" />
              </span>
            </div>

            {/* Titles & Metadata */}
            <div className="min-w-0 space-y-1.5 sm:space-y-2">
              <div className="flex items-center gap-2 flex-wrap">
                <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-text-primary font-display truncate">
                  Matched Opportunities
                </h1>
                <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full border border-emerald-500/30 bg-emerald-500/10 text-emerald-400 text-[11px] font-medium shrink-0">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                  <span>Pipeline Active</span>
                </span>
              </div>

              <div className="text-xs sm:text-sm text-text-secondary font-medium flex items-center gap-2 flex-wrap">
                <span className="text-text-primary font-semibold">{stats.total} Ingested Signals</span>
                <span className="text-text-muted">•</span>
                <span className="text-text-muted">{stats.remotePercentage}% Remote</span>
                <span className="text-text-muted">•</span>
                <span className="font-mono text-xs text-accent">{stats.highMatches} Prime Matches (≥80%)</span>
              </div>

              <p className="text-xs text-text-muted leading-relaxed line-clamp-1 sm:line-clamp-none">
                Continuous intent signals ingested across Hacker News, Remotive, and Arbeitnow matching your verified profile.
              </p>
            </div>
          </div>

          {/* Right Action / Feedback */}
          <div className="flex sm:flex-col items-end justify-between sm:justify-center gap-2.5 shrink-0 pt-3 sm:pt-0 border-t sm:border-t-0 border-border/40">
            <div className="inline-flex items-center gap-1.5 text-[10px] font-mono text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 px-2.5 py-1 rounded-md">
              <Sparkles className="w-3 h-3 text-emerald-400 animate-pulse shrink-0" />
              <span>Real-Time Sync</span>
            </div>
          </div>
        </div>
      </div>

      {/* Filter Toolbar */}
      <FilterToolbar
        className="relative z-30"
        filters={filters}
        onFilterChange={handleFilterChange}
        onTriggerDiscovery={handleTriggerDiscovery}
        isDiscovering={isDiscovering}
        totalCount={leads.length}
        filteredCount={filteredLeads.length}
      />

      {/* Leads List or Zero State */}
      {filteredLeads.length > 0 ? (
        <div className="space-y-4 sm:space-y-5 relative z-10">
          {paginatedLeads.map((lead) => (
            <LeadCard
              key={lead.id}
              lead={lead}
              isSelected={selectedLead?.id === lead.id}
              onSelect={handleSelectLead}
            />
          ))}

          {/* Luxury Editorial Pagination (Larger Screens Only) */}
          {totalPages > 1 && (
            <div className="hidden sm:flex items-center justify-between rounded-2xl border border-zinc-800/80 bg-surface/90 backdrop-blur-xl px-5 py-4 shadow-xl shadow-black/20 w-full mt-6">
              {/* Range Counter */}
              <div className="text-xs text-text-muted font-sans flex items-center gap-1.5">
                <span>Showing</span>
                <span className="font-mono font-semibold text-text-primary">
                  {(safeCurrentPage - 1) * pageSize + 1}-{Math.min(safeCurrentPage * pageSize, filteredLeads.length)}
                </span>
                <span>of</span>
                <span className="font-mono font-semibold text-text-primary">{filteredLeads.length}</span>
                <span>opportunities</span>
              </div>

              {/* Page Controls */}
              <div className="flex items-center gap-2 select-none">
                <button
                  type="button"
                  onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                  disabled={safeCurrentPage === 1}
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl border border-zinc-800 bg-zinc-900/60 hover:bg-surface-hover text-xs font-medium text-text-secondary hover:text-text-primary disabled:opacity-40 disabled:pointer-events-none transition-colors"
                >
                  <ChevronLeft className="w-3.5 h-3.5" />
                  <span>Previous</span>
                </button>

                <div className="flex items-center gap-1.5">
                  {Array.from({ length: totalPages }, (_, i) => i + 1).map((page) => (
                    <button
                      key={page}
                      type="button"
                      onClick={() => setCurrentPage(page)}
                      className={cn(
                        'w-8 h-8 rounded-xl text-xs font-mono font-medium transition-all flex items-center justify-center border',
                        safeCurrentPage === page
                          ? 'border-accent bg-accent text-white shadow-md shadow-accent/25 font-bold'
                          : 'border-zinc-800 bg-zinc-900/60 hover:bg-surface-hover text-text-secondary hover:text-text-primary'
                      )}
                    >
                      {page}
                    </button>
                  ))}
                </div>

                <button
                  type="button"
                  onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
                  disabled={safeCurrentPage === totalPages}
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl border border-zinc-800 bg-zinc-900/60 hover:bg-surface-hover text-xs font-medium text-text-secondary hover:text-text-primary disabled:opacity-40 disabled:pointer-events-none transition-colors"
                >
                  <span>Next</span>
                  <ChevronRight className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          )}
        </div>
      ) : (
        <EmptyState
          title="No opportunities found"
          description="No hiring leads match your current search and filter criteria. Try adjusting the score threshold or clearing your search term."
          actionLabel="Reset All Filters"
          onAction={handleResetFilters}
          className="my-10"
        />
      )}

      {/* Slide-Over Detail Drawer */}
      <LeadDetailDrawer
        lead={selectedLead}
        isOpen={isDrawerOpen}
        onClose={handleCloseDrawer}
        onPrepareOutreach={onPrepareOutreach}
      />
    </div>
  )
}
