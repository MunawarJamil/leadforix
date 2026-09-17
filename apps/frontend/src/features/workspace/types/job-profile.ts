/**
 * TypeScript domain models for Workspace & Job Seeker Profile.
 *
 * Matches backend schemas in `apps/services/workspace_service/app/api/schemas.py`
 * and domain models in `apps/services/workspace_service/app/domain/roles.py`.
 */

export type ExperienceLevel =
  | 'ENTRY'
  | 'MID'
  | 'SENIOR'
  | 'LEAD'
  | 'ARCHITECT'
  | 'EXPERT'

export type JobSearchStatus =
  | 'ACTIVELY_LOOKING'
  | 'OPEN_TO_OFFERS'
  | 'NOT_LOOKING'

export interface JobProfile {
  id: string
  user_id: string
  workspace_id: string
  target_titles: string[]
  primary_skills: string[]
  target_locations: string[]
  is_remote_only: boolean
  experience_level: ExperienceLevel
  min_salary_usd: number | null
  search_status: JobSearchStatus
  created_at: string
  updated_at: string
}

export interface UpdateJobProfilePayload {
  target_titles?: string[]
  primary_skills?: string[]
  target_locations?: string[]
  is_remote_only?: boolean
  experience_level?: ExperienceLevel
  min_salary_usd?: number | null
  search_status?: JobSearchStatus
}
