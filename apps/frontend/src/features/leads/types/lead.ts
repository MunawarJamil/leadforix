/**
 * TypeScript domain types for Lead Discovery and Ingestion.
 *
 * Matches backend `LeadModel` from `apps/services/lead_service/app/infrastructure/models.py`.
 */

export type LeadSource = 'hacker_news' | 'remotive' | 'arbeitnow'

export type LeadStatus =
  | 'NEW'
  | 'QUALIFIED'
  | 'DISQUALIFIED'
  | 'CONTACTED'
  | 'ARCHIVED'

export interface Lead {
  id: string
  company_name: string
  title: string
  description: string
  source: LeadSource
  source_url: string
  source_id: string
  location: string | null
  is_remote: boolean
  salary_info: string | null
  match_score: number
  matched_skills: string[]
  status: LeadStatus
  posted_at: string | null
  discovered_at: string
}

export interface LeadFilterState {
  searchQuery: string
  source: 'ALL' | LeadSource
  minScore: number
  remoteOnly: boolean
  status: 'ALL' | LeadStatus
}
