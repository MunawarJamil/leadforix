import * as React from 'react'
import { zodResolver } from '@hookform/resolvers/zod'
import {
  Briefcase,
  CheckCircle2,
  DollarSign,
  Globe2,
  Layers,
  Save,
  Sparkles,
} from 'lucide-react'
import { Controller, useForm } from 'react-hook-form'
import { Button } from '@/components/ui/button'
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { cn } from '@/lib/utils'
import {
  jobProfileSchema,
  type JobProfileFormData,
} from '../schemas/job-profile-schema'
import type { ExperienceLevel, JobProfile, JobSearchStatus } from '../types/job-profile'
import { SkillTagPicker } from './skill-tag-picker'

const POPULAR_SKILL_SUGGESTIONS = [
  'Python',
  'FastAPI',
  'PostgreSQL',
  'TypeScript',
  'React',
  'Docker',
  'Redis',
  'LangChain',
  'Qdrant',
  'Go',
  'AWS',
  'Celery',
  'Next.js',
  'TailwindCSS',
]

const POPULAR_TITLE_SUGGESTIONS = [
  'Senior Backend Engineer',
  'Fullstack Developer',
  'AI / ML Engineer',
  'Lead Software Architect',
  'DevOps / SRE',
]

const EXPERIENCE_LEVELS: { id: ExperienceLevel; label: string; range: string }[] = [
  { id: 'ENTRY', label: 'Entry', range: '0–2 yrs' },
  { id: 'MID', label: 'Mid-Level', range: '2–5 yrs' },
  { id: 'SENIOR', label: 'Senior', range: '5–8 yrs' },
  { id: 'LEAD', label: 'Lead', range: '8+ yrs' },
  { id: 'ARCHITECT', label: 'Architect', range: '10+ yrs' },
  { id: 'EXPERT', label: 'Expert / Staff', range: '12+ yrs' },
]

const SEARCH_STATUSES: {
  id: JobSearchStatus
  label: string
  desc: string
  color: string
}[] = [
  {
    id: 'ACTIVELY_LOOKING',
    label: 'Actively Looking',
    desc: 'Ready for high-intent interviews and instant applications',
    color: 'border-success text-success bg-success/10',
  },
  {
    id: 'OPEN_TO_OFFERS',
    label: 'Open to Offers',
    desc: 'Passively evaluating exceptional remote opportunities',
    color: 'border-accent text-accent bg-accent/10',
  },
  {
    id: 'NOT_LOOKING',
    label: 'Not Looking',
    desc: 'Pausing lead matching and outreach triggers',
    color: 'border-border text-text-muted bg-surface',
  },
]

export interface JobProfileFormProps {
  initialData?: Partial<JobProfile>
  onSubmit?: (data: JobProfileFormData) => Promise<void> | void
  isLoading?: boolean
  className?: string
}

export const JobProfileForm: React.FC<JobProfileFormProps> = ({
  initialData,
  onSubmit,
  isLoading = false,
  className,
}) => {
  const [saveSuccess, setSaveSuccess] = React.useState(false)

  const defaultValues: JobProfileFormData = {
    target_titles: initialData?.target_titles || ['Fullstack Engineer'],
    primary_skills: initialData?.primary_skills || ['Python', 'FastAPI', 'React', 'PostgreSQL'],
    target_locations: initialData?.target_locations || ['Remote', 'United States'],
    is_remote_only: initialData?.is_remote_only ?? true,
    experience_level: initialData?.experience_level || 'SENIOR',
    min_salary_usd: initialData?.min_salary_usd ?? 120000,
    search_status: initialData?.search_status || 'ACTIVELY_LOOKING',
  }

  const {
    register,
    control,
    handleSubmit,
    formState: { errors, isDirty, isSubmitting },
  } = useForm<JobProfileFormData>({
    resolver: zodResolver(jobProfileSchema),
    defaultValues,
  })

  const onFormSubmit = async (data: JobProfileFormData) => {
    try {
      if (onSubmit) {
        await onSubmit(data)
      }
      setSaveSuccess(true)
      setTimeout(() => setSaveSuccess(false), 4000)
    } catch (err) {
      console.error('Failed to save job profile:', err)
    }
  }

  return (
    <form
      onSubmit={handleSubmit(onFormSubmit)}
      className={cn('space-y-8 max-w-4xl mx-auto', className)}
    >
      {/* Header Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-border pb-6">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-border bg-surface text-accent text-xs font-semibold mb-2">
            <Sparkles className="w-3.5 h-3.5" />
            <span>AI Matching Profile</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-text-primary">
            Job Seeker & Skill Profile
          </h1>
          <p className="text-sm text-text-secondary mt-1">
            Leadforix scoring engines match public hiring posts directly against your primary skills and desired titles.
          </p>
        </div>

        {/* Status Pill */}
        <div className="flex items-center gap-3">
          {saveSuccess && (
            <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-success-muted text-success border border-success/20 text-xs font-medium animate-fade-in">
              <CheckCircle2 className="w-4 h-4" />
              <span>Profile updated successfully!</span>
            </div>
          )}
          <Button
            type="submit"
            isLoading={isLoading || isSubmitting}
            disabled={!isDirty && !saveSuccess}
            leftIcon={<Save className="w-4 h-4" />}
            size="default"
          >
            Save Profile
          </Button>
        </div>
      </div>

      {/* 1. Target Roles & Seniority */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2 text-accent text-sm font-medium">
            <Briefcase className="w-4 h-4" />
            <span>Role Preferences</span>
          </div>
          <CardTitle>Target Roles & Experience Level</CardTitle>
          <CardDescription>
            Specify the job titles you want the pipeline to surface and your seniority tier.
          </CardDescription>
        </CardHeader>

        <CardContent className="space-y-6">
          {/* Target Titles Tag Picker */}
          <Controller
            name="target_titles"
            control={control}
            render={({ field }) => (
              <SkillTagPicker
                label="Target Job Titles"
                description="Roles you are actively seeking (e.g. Senior Backend Engineer, AI Engineer)"
                value={field.value}
                onChange={field.onChange}
                suggestions={POPULAR_TITLE_SUGGESTIONS}
                placeholder="Type a target job title and press Enter..."
                error={errors.target_titles?.message}
                maxTags={5}
              />
            )}
          />

          {/* Experience Level Selector */}
          <div className="space-y-2">
            <label className="text-sm font-medium text-text-primary">
              Seniority Level
            </label>
            <Controller
              name="experience_level"
              control={control}
              render={({ field }) => (
                <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-2.5">
                  {EXPERIENCE_LEVELS.map((level) => {
                    const isSelected = field.value === level.id
                    return (
                      <button
                        key={level.id}
                        type="button"
                        onClick={() => field.onChange(level.id)}
                        className={cn(
                          'flex flex-col items-center justify-center p-3 rounded-lg border text-center transition-all',
                          isSelected
                            ? 'border-accent bg-accent/15 text-text-primary shadow-sm shadow-accent/20'
                            : 'border-border bg-surface hover:bg-surface-hover text-text-secondary hover:text-text-primary'
                        )}
                      >
                        <span className="text-xs font-semibold">{level.label}</span>
                        <span className="text-[11px] text-text-muted mt-0.5">{level.range}</span>
                      </button>
                    )
                  })}
                </div>
              )}
            />
            {errors.experience_level && (
              <p className="text-xs text-error mt-1">{errors.experience_level.message}</p>
            )}
          </div>
        </CardContent>
      </Card>

      {/* 2. Core Technical Stack & Skills */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2 text-accent text-sm font-medium">
            <Layers className="w-4 h-4" />
            <span>Matching Engine Intelligence</span>
          </div>
          <CardTitle>Primary Technical Skills</CardTitle>
          <CardDescription>
            The scoring algorithm calculates match scores (0–100%) by correlating these skills with public lead descriptions.
          </CardDescription>
        </CardHeader>

        <CardContent>
          <Controller
            name="primary_skills"
            control={control}
            render={({ field }) => (
              <SkillTagPicker
                label="Core Skills & Technologies"
                description="Languages, frameworks, databases, and tools you excel at."
                value={field.value}
                onChange={field.onChange}
                suggestions={POPULAR_SKILL_SUGGESTIONS}
                placeholder="Type a skill (e.g. Python, Docker, LangChain) and press Enter..."
                error={errors.primary_skills?.message}
                maxTags={25}
              />
            )}
          />
        </CardContent>
      </Card>

      {/* 3. Compensation & Discovery Filters */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2 text-accent text-sm font-medium">
            <Globe2 className="w-4 h-4" />
            <span>Search & Availability</span>
          </div>
          <CardTitle>Compensation & Search Status</CardTitle>
          <CardDescription>
            Filter incoming opportunities by minimum salary floor, remote flexibility, and intent.
          </CardDescription>
        </CardHeader>

        <CardContent className="space-y-6">
          {/* Search Status Segmented Cards */}
          <div className="space-y-2">
            <label className="text-sm font-medium text-text-primary">
              Current Job Search Status
            </label>
            <Controller
              name="search_status"
              control={control}
              render={({ field }) => (
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                  {SEARCH_STATUSES.map((status) => {
                    const isSelected = field.value === status.id
                    return (
                      <button
                        key={status.id}
                        type="button"
                        onClick={() => field.onChange(status.id)}
                        className={cn(
                          'p-4 rounded-xl border text-left transition-all',
                          isSelected
                            ? 'border-accent bg-accent/10 shadow-sm shadow-accent/20 ring-1 ring-accent'
                            : 'border-border bg-surface hover:bg-surface-hover'
                        )}
                      >
                        <div className="flex items-center justify-between mb-1.5">
                          <span className="text-sm font-bold text-text-primary">
                            {status.label}
                          </span>
                          {isSelected && (
                            <span className="w-2 h-2 rounded-full bg-accent animate-pulse" />
                          )}
                        </div>
                        <p className="text-xs text-text-secondary leading-relaxed">
                          {status.desc}
                        </p>
                      </button>
                    )
                  })}
                </div>
              )}
            />
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 pt-2">
            {/* Min Salary Input */}
            <div className="space-y-1.5">
              <label className="text-sm font-medium text-text-primary">
                Minimum Annual Compensation (USD)
              </label>
              <Input
                type="number"
                step={5000}
                min={0}
                placeholder="120000"
                leftIcon={<DollarSign className="w-4 h-4 text-text-muted" />}
                error={errors.min_salary_usd?.message}
                {...register('min_salary_usd', { valueAsNumber: true })}
              />
              <p className="text-xs text-text-muted">
                Leads with compensation below this baseline will be deprioritized.
              </p>
            </div>

            {/* Remote Only Toggle */}
            <div className="space-y-1.5">
              <label className="text-sm font-medium text-text-primary">
                Workplace Flexibility
              </label>
              <div className="p-3.5 rounded-lg border border-border bg-surface flex items-center justify-between">
                <div>
                  <span className="text-sm font-medium text-text-primary block">
                    Remote Opportunities Only
                  </span>
                  <span className="text-xs text-text-secondary block">
                    Exclude jobs that mandate physical on-site presence
                  </span>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    className="sr-only peer"
                    {...register('is_remote_only')}
                  />
                  <div className="w-11 h-6 bg-border peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-border after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-accent"></div>
                </label>
              </div>
            </div>
          </div>

          {/* Target Locations */}
          <Controller
            name="target_locations"
            control={control}
            render={({ field }) => (
              <SkillTagPicker
                label="Preferred Geographic Locations"
                description="Regions or countries you are authorized to work in (e.g. Remote, US, EU, Canada)"
                value={field.value}
                onChange={field.onChange}
                suggestions={['Remote', 'United States', 'Europe', 'Canada', 'United Kingdom']}
                placeholder="Type location and press Enter..."
                maxTags={8}
              />
            )}
          />
        </CardContent>

        <CardFooter className="flex items-center justify-between border-t border-border pt-4">
          <span className="text-xs text-text-muted">
            {isDirty ? (
              <span className="text-warning font-medium">● You have unsaved changes</span>
            ) : (
              'All changes saved'
            )}
          </span>
          <Button
            type="submit"
            isLoading={isLoading || isSubmitting}
            disabled={!isDirty && !saveSuccess}
            leftIcon={<Save className="w-4 h-4" />}
          >
            Save Profile
          </Button>
        </CardFooter>
      </Card>
    </form>
  )
}
