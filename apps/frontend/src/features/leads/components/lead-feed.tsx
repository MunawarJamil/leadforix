import * as React from 'react'
import { Sparkles } from 'lucide-react'
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

  const [filters, setFilters] = React.useState<LeadFilterState>({
    searchQuery: '',
    source: 'ALL',
    minScore: 0,
    remoteOnly: false,
    status: 'ALL',
  })

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

      // 4. Remote only
      if (filters.remoteOnly && !lead.is_remote) {
        return false
      }

      // 5. Status filter
      if (filters.status !== 'ALL' && lead.status !== filters.status) {
        return false
      }

      return true
    })
  }, [leads, filters])

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
    }, 2000)
  }

  const handleResetFilters = () => {
    setFilters({
      searchQuery: '',
      source: 'ALL',
      minScore: 0,
      remoteOnly: false,
      status: 'ALL',
    })
  }

  return (
    <div className={cn('space-y-6 max-w-5xl mx-auto', className)}>
      {/* Header Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-border pb-6">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-border bg-surface text-accent text-xs font-semibold mb-2">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Public Intent Signals</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-text-primary">
            Matched Lead Feed
          </h1>
          <p className="text-sm text-text-secondary mt-1">
            Real-time hiring opportunities continuously ingested from Hacker News, Remotive, and Arbeitnow.
          </p>
        </div>
      </div>

      {/* Filter Toolbar */}
      <FilterToolbar
        filters={filters}
        onFilterChange={setFilters}
        onTriggerDiscovery={handleTriggerDiscovery}
        isDiscovering={isDiscovering}
        totalCount={leads.length}
        filteredCount={filteredLeads.length}
      />

      {/* Leads List or Zero State */}
      {filteredLeads.length > 0 ? (
        <div className="space-y-3.5">
          {filteredLeads.map((lead) => (
            <LeadCard
              key={lead.id}
              lead={lead}
              isSelected={selectedLead?.id === lead.id}
              onSelect={handleSelectLead}
            />
          ))}
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
