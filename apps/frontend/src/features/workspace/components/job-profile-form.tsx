import * as React from 'react'
import { zodResolver } from '@hookform/resolvers/zod'
import {
  Briefcase,
  Check,
  CheckCircle2,
  Compass,
  DollarSign,
  Globe2,
  Layers,
  MapPin,
  Pencil,
  Save,
  Sparkles,
  Tag,
  X,
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
import { cn } from '@/lib/utils'
import {
  jobProfileSchema,
  type JobProfileFormData,
} from '../schemas/job-profile-schema'
import type { ExperienceLevel, JobProfile, JobSearchStatus } from '../types/job-profile'
import { SkillTagPicker } from './skill-tag-picker'

const CATEGORIZED_SKILL_SUGGESTIONS = [
  {
    category: 'Backend & Core Languages',
    items: ['Python', 'FastAPI', 'TypeScript', 'Node.js', 'Go', 'Rust'],
  },
  {
    category: 'AI, LLM & Vector Systems',
    items: ['LangChain', 'LangGraph', 'Qdrant', 'RAG', 'OpenAI', 'PyTorch'],
  },
  {
    category: 'Databases & Cloud Infra',
    items: ['PostgreSQL', 'Docker', 'Redis', 'Kubernetes', 'AWS', 'Celery'],
  },
  {
    category: 'Frontend & Fullstack',
    items: ['React', 'Next.js', 'TailwindCSS', 'GraphQL'],
  },
]

const POPULAR_TITLE_SUGGESTIONS = [
  'Senior Backend Engineer',
  'Fullstack Developer',
  'AI / ML Engineer',
  'Lead Software Architect',
  'DevOps / SRE',
  'Data Engineer',
]

const POPULAR_LOCATION_SUGGESTIONS = [
  'Remote',
  'United States',
  'Europe',
  'United Kingdom',
  'Canada',
  'Worldwide',
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
  tag: string
  activeBorder: string
  activeBg: string
  badgeColor: string
}[] = [
  {
    id: 'ACTIVELY_LOOKING',
    label: 'Actively Looking',
    desc: 'Ready for high-intent interviews, rapid screening, and instant match notifications.',
    tag: 'Highest Priority',
    activeBorder: 'border-emerald-500/80',
    activeBg: 'bg-emerald-950/20',
    badgeColor: 'border-emerald-500/40 bg-emerald-500/10 text-emerald-400',
  },
  {
    id: 'OPEN_TO_OFFERS',
    label: 'Open to Offers',
    desc: 'Passively evaluating exceptional opportunities matching your compensation baseline.',
    tag: 'Selective Mode',
    activeBorder: 'border-accent/80',
    activeBg: 'bg-accent/10',
    badgeColor: 'border-accent/40 bg-accent/10 text-accent',
  },
  {
    id: 'NOT_LOOKING',
    label: 'Not Looking',
    desc: 'Temporarily pausing automated lead matching algorithms and outreach pipelines.',
    tag: 'Paused Pipeline',
    activeBorder: 'border-zinc-700',
    activeBg: 'bg-zinc-900/40',
    badgeColor: 'border-zinc-700 bg-zinc-800 text-zinc-400',
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
  const [isEditingRoles, setIsEditingRoles] = React.useState(false)
  const [isEditingSkills, setIsEditingSkills] = React.useState(false)
  const [isEditingSearch, setIsEditingSearch] = React.useState(false)

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
    watch,
    trigger,
    formState: { errors, isDirty, isSubmitting },
  } = useForm<JobProfileFormData>({
    resolver: zodResolver(jobProfileSchema),
    defaultValues,
  })

  const currentTargetTitles = watch('target_titles')
  const currentExperienceLevel = watch('experience_level')
  const selectedLevelObj =
    EXPERIENCE_LEVELS.find((l) => l.id === currentExperienceLevel) || EXPERIENCE_LEVELS[2]

  const currentPrimarySkills = watch('primary_skills')
  const currentSearchStatus = watch('search_status')
  const currentSalary = watch('min_salary_usd')
  const currentRemoteOnly = watch('is_remote_only')
  const currentLocations = watch('target_locations')
  const selectedStatusObj =
    SEARCH_STATUSES.find((s) => s.id === currentSearchStatus) || SEARCH_STATUSES[0]

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
      className={cn('space-y-8 max-w-4xl mx-auto w-full min-w-0', className)}
    >
      {/* Munawar Minhas Identity Header Banner */}
      <div className="relative overflow-hidden rounded-2xl border border-zinc-800/80 bg-surface/90 backdrop-blur-xl p-5 sm:p-7 shadow-xl shadow-black/30 w-full">
        <div
          aria-hidden="true"
          className="pointer-events-none absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r from-transparent via-accent to-transparent opacity-80"
        />
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-5">
          {/* User Info */}
          <div className="flex items-center gap-4 sm:gap-5 min-w-0">
            {/* Avatar */}
            <div className="relative flex h-14 w-14 sm:h-18 sm:w-18 shrink-0 items-center justify-center rounded-2xl bg-gradient-to-br from-accent/25 via-accent/10 to-surface border border-accent/40 shadow-lg shadow-accent/20">
              <span className="text-lg sm:text-xl font-bold font-mono tracking-tight text-accent">
                MM
              </span>
              <span className="absolute -bottom-1 -right-1 flex h-3.5 w-3.5 sm:h-4 sm:w-4">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
                <span className="relative inline-flex rounded-full h-3.5 w-3.5 sm:h-4 sm:w-4 bg-emerald-500 border-2 border-surface" />
              </span>
            </div>

            {/* Titles */}
            <div className="min-w-0">
              <div className="flex items-center gap-2 flex-wrap">
                <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-text-primary font-display truncate">
                  Munawar Minhas
                </h1>
                <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full border border-emerald-500/30 bg-emerald-500/10 text-emerald-400 text-[11px] font-medium shrink-0">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                  <span>Actively Looking</span>
                </span>
              </div>

              <div className="text-xs sm:text-sm text-text-secondary mt-1 font-medium flex items-center gap-2 flex-wrap">
                <span className="text-text-primary font-semibold">Fullstack Platform Engineer</span>
                <span className="text-text-muted">•</span>
                <span className="text-text-muted">Remote · Global</span>
                <span className="text-text-muted">•</span>
                <span className="font-mono text-xs text-accent">Senior (5–8 yrs)</span>
              </div>

              <p className="text-xs text-text-muted mt-1.5 line-clamp-1 sm:line-clamp-none">
                Scoring engines match HN, Remotive, and Arbeitnow leads against your verified skill vector.
              </p>
            </div>
          </div>

          {/* Right Action / Feedback */}
          <div className="flex sm:flex-col items-end justify-between sm:justify-center gap-2.5 shrink-0 pt-3 sm:pt-0 border-t sm:border-t-0 border-border/40">
            <div className="inline-flex items-center gap-1.5 text-[10px] font-mono text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 px-2.5 py-1 rounded-md">
              <Sparkles className="w-3 h-3 text-emerald-400 animate-pulse shrink-0" />
              <span>Matching Active</span>
            </div>
            {saveSuccess && (
              <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-success-muted text-success border border-success/20 text-xs font-medium animate-fade-in">
                <CheckCircle2 className="w-3.5 h-3.5" />
                <span>Saved</span>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* 1. Target Roles & Seniority */}
      <Card className={cn(
        "relative transition-all duration-300 overflow-hidden w-full min-w-0",
        isEditingRoles
          ? "border-accent/60 bg-surface/95 shadow-xl shadow-accent/10 ring-1 ring-accent/30"
          : "border-zinc-800/80 bg-surface/90 hover:border-zinc-700/80"
      )}>
        {/* Active Top Accent Glow Beam */}
        {isEditingRoles && (
          <div
            aria-hidden="true"
            className="pointer-events-none absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r from-transparent via-accent to-transparent opacity-100 animate-fade-in"
          />
        )}

        <CardHeader className="p-4 sm:p-6 pb-3 sm:pb-4">
          {/* Top Row: Eyebrow + Status on left, Actions on right */}
          <div className="flex items-center justify-between gap-2 w-full">
            <div className="flex items-center gap-2 text-accent text-xs sm:text-sm font-medium min-w-0">
              <Briefcase className="w-3.5 h-3.5 sm:w-4 sm:h-4 shrink-0" />
              <span className="font-semibold tracking-wide truncate">Role Preferences</span>
              {isEditingRoles && (
                <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[10px] font-mono font-semibold bg-accent/15 text-accent border border-accent/30 shrink-0">
                  <span className="w-1.5 h-1.5 rounded-full bg-accent animate-ping" />
                  <span>EDITING</span>
                </span>
              )}
            </div>

            {/* Toggle Edit / Save Buttons */}
            {!isEditingRoles ? (
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={() => setIsEditingRoles(true)}
                className="border-zinc-800 bg-zinc-900/80 hover:bg-zinc-800 hover:border-accent/50 hover:text-accent gap-1.5 text-xs h-7 sm:h-8 px-2.5 sm:px-3.5 shrink-0 transition-all shadow-sm"
              >
                <Pencil className="w-3 h-3 sm:w-3.5 sm:h-3.5" />
                <span>Edit</span>
              </Button>
            ) : (
              <div className="flex items-center gap-1.5 sm:gap-2 shrink-0">
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  onClick={() => setIsEditingRoles(false)}
                  className="text-xs h-7 sm:h-8 px-2 sm:px-3 text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800/60 gap-1 transition-colors"
                >
                  <X className="w-3 h-3 sm:w-3.5 sm:h-3.5" />
                  <span>Cancel</span>
                </Button>
                <Button
                  type="button"
                  size="sm"
                  onClick={async () => {
                    const isValid = await trigger(['target_titles', 'experience_level'])
                    if (isValid) {
                      setIsEditingRoles(false)
                      handleSubmit(onFormSubmit)()
                    }
                  }}
                  className="btn-shine text-xs h-7 sm:h-8 px-3 sm:px-4 gap-1 sm:gap-1.5 shadow-glow font-semibold bg-accent hover:bg-accent/90 text-white transition-all"
                >
                  <Check className="w-3 h-3 sm:w-3.5 sm:h-3.5" />
                  <span>Done</span>
                </Button>
              </div>
            )}
          </div>

          {/* Full-width Title and Description */}
          <div className="mt-2 sm:mt-2.5">
            <CardTitle className="text-xl sm:text-2xl font-bold tracking-tight text-text-primary font-display">
              Target Roles & Experience Level
            </CardTitle>
            <CardDescription className="text-xs sm:text-sm mt-1 text-zinc-400 leading-relaxed">
              Specify the job titles you want the pipeline to surface and your seniority tier.
            </CardDescription>
          </div>
        </CardHeader>

        <CardContent className="p-4 sm:p-6 pt-0 sm:pt-0 space-y-5 sm:space-y-6">
          {/* VIEW MODE: Clean, only selected data, NO SUGGESTIONS */}
          {!isEditingRoles ? (
            <div className="space-y-5 sm:space-y-6 animate-fade-in">
              {/* Selected Target Job Titles */}
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <label className="text-sm font-semibold text-zinc-200 flex items-center gap-1.5">
                    <Tag className="w-3.5 h-3.5 text-accent" />
                    <span>Target Job Titles</span>
                  </label>
                  <span className="text-xs text-zinc-400 font-mono bg-zinc-900 px-2.5 py-1 rounded-md border border-zinc-800">
                    {currentTargetTitles?.length || 0} active roles
                  </span>
                </div>
                {currentTargetTitles && currentTargetTitles.length > 0 ? (
                  <div className="flex flex-wrap items-center gap-2">
                    {currentTargetTitles.map((title) => (
                      <span
                        key={title}
                        className="inline-flex items-center px-3 py-1.5 rounded-lg border border-accent/40 bg-accent/10 text-accent text-xs font-semibold shadow-sm shadow-accent/5 transition-all"
                      >
                        {title}
                      </span>
                    ))}
                  </div>
                ) : (
                  <p className="text-xs text-zinc-500 italic">No target titles specified yet.</p>
                )}
              </div>

              {/* Selected Seniority Level - ONLY Show Selected Card, Hide All Others */}
              <div className="space-y-2">
                <label className="text-sm font-semibold text-zinc-200 flex items-center gap-1.5">
                  <Briefcase className="w-3.5 h-3.5 text-accent" />
                  <span>Seniority Level</span>
                </label>
                <div className="p-4 rounded-xl border border-accent/40 bg-accent/10 shadow-sm shadow-accent/10 max-w-xl flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-accent/20 border border-accent/30 flex items-center justify-center text-accent shrink-0">
                      <CheckCircle2 className="w-4 h-4" />
                    </div>
                    <div>
                      <div className="text-sm font-bold text-white flex items-center gap-2">
                        <span>{selectedLevelObj.label}</span>
                        <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                      </div>
                      <div className="text-xs text-zinc-400 font-mono mt-0.5">
                        {selectedLevelObj.range} experience
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ) : (
            /* EDIT MODE: Interactive tag picker with quick-add chips + polished 6-card grid */
            <div className="space-y-6 animate-fade-in p-1">
              {/* Target Titles Tag Picker with suggestions */}
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
                    suggestionsLabel="Suggested Role Titles:"
                    placeholder="Type a target job title and press Enter..."
                    error={errors.target_titles?.message}
                    maxTags={5}
                  />
                )}
              />

              {/* Seniority Level 6-Card Selector with high-contrast active tiles */}
              <div className="space-y-2 pt-1">
                <div className="flex items-center justify-between">
                  <label className="text-sm font-semibold text-zinc-200 block">
                    Seniority Tier
                  </label>
                  <span className="text-[11px] font-mono text-accent">
                    {selectedLevelObj.label} ({selectedLevelObj.range})
                  </span>
                </div>
                <p className="text-xs text-zinc-400">
                  Select the tier you want matching models to prioritize.
                </p>
                <Controller
                  name="experience_level"
                  control={control}
                  render={({ field }) => (
                    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2.5 pt-1">
                      {EXPERIENCE_LEVELS.map((level) => {
                        const isSelected = field.value === level.id
                        return (
                          <button
                            key={level.id}
                            type="button"
                            onClick={() => field.onChange(level.id)}
                            className={cn(
                              'relative flex flex-col items-center justify-center p-3.5 rounded-xl border text-center transition-all duration-200 cursor-pointer group',
                              isSelected
                                ? 'border-accent bg-gradient-to-b from-accent/25 via-accent/10 to-zinc-950/90 text-white shadow-[0_0_16px_rgba(99,102,241,0.25)] ring-1 ring-accent/60 scale-[1.02]'
                                : 'border-zinc-800/80 bg-zinc-950/40 hover:bg-zinc-900/60 hover:border-zinc-700 text-zinc-400 hover:text-zinc-200'
                            )}
                          >
                            {isSelected && (
                              <span className="w-1.5 h-1.5 rounded-full bg-accent absolute top-2 right-2 animate-ping" />
                            )}
                            <span className="text-xs font-bold tracking-tight">{level.label}</span>
                            <span className={cn(
                              "text-[10px] font-mono px-2 py-0.5 rounded-full mt-1.5 border transition-colors",
                              isSelected
                                ? "bg-accent/20 border-accent/40 text-accent font-semibold"
                                : "bg-black/50 border-white/5 text-zinc-500 group-hover:text-zinc-400"
                            )}>
                              {level.range}
                            </span>
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
            </div>
          )}
        </CardContent>

        {/* Save Preferences: Only visible when this section is in edit mode */}
        {isEditingRoles && (
          <CardFooter className="flex flex-col sm:flex-row items-center justify-between border-t border-zinc-800/80 pt-4 gap-3 animate-fade-in">
            <span className="text-xs text-zinc-400">
              {isDirty ? (
                <span className="text-amber-400 font-medium flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-amber-400 animate-pulse" />
                  <span>You have unsaved changes</span>
                </span>
              ) : (
                <span className="text-zinc-500 flex items-center gap-1.5">
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                  <span>All profile preferences in sync</span>
                </span>
              )}
            </span>
            <Button
              type="submit"
              isLoading={isLoading || isSubmitting}
              disabled={!isDirty && !saveSuccess}
              leftIcon={<Save className="w-4 h-4" />}
              className="btn-shine shadow-glow hover:shadow-glow-lg w-full sm:w-auto"
            >
              Save All Preferences
            </Button>
          </CardFooter>
        )}
      </Card>

      {/* 2. Core Technical Stack & Skills */}
      <Card className={cn(
        "relative transition-all duration-300 overflow-hidden w-full min-w-0",
        isEditingSkills
          ? "border-accent/60 bg-surface/95 shadow-xl shadow-accent/10 ring-1 ring-accent/30"
          : "border-zinc-800/80 bg-surface/90 hover:border-zinc-700/80"
      )}>
        {/* Active Top Accent Glow Beam */}
        {isEditingSkills && (
          <div
            aria-hidden="true"
            className="pointer-events-none absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r from-transparent via-accent to-transparent opacity-100 animate-fade-in"
          />
        )}

        <CardHeader className="p-4 sm:p-6 pb-3 sm:pb-4">
          {/* Top Row: Eyebrow + Status on left, Actions on right */}
          <div className="flex items-center justify-between gap-2 w-full">
            <div className="flex items-center gap-2 text-accent text-xs sm:text-sm font-medium min-w-0">
              <Layers className="w-3.5 h-3.5 sm:w-4 sm:h-4 shrink-0" />
              <span className="font-semibold tracking-wide truncate">Matching Engine Intelligence</span>
              {isEditingSkills && (
                <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[10px] font-mono font-semibold bg-accent/15 text-accent border border-accent/30 shrink-0">
                  <span className="w-1.5 h-1.5 rounded-full bg-accent animate-ping" />
                  <span>EDITING</span>
                </span>
              )}
            </div>

            {/* Edit / Done Buttons */}
            {!isEditingSkills ? (
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={() => setIsEditingSkills(true)}
                className="border-zinc-800 bg-zinc-900/80 hover:bg-zinc-800 hover:border-accent/50 hover:text-accent gap-1.5 text-xs h-7 sm:h-8 px-2.5 sm:px-3.5 shrink-0 transition-all shadow-sm"
              >
                <Pencil className="w-3 h-3 sm:w-3.5 sm:h-3.5" />
                <span>Edit</span>
              </Button>
            ) : (
              <div className="flex items-center gap-1.5 sm:gap-2 shrink-0">
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  onClick={() => setIsEditingSkills(false)}
                  className="text-xs h-7 sm:h-8 px-2 sm:px-3 text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800/60 gap-1 transition-colors"
                >
                  <X className="w-3 h-3 sm:w-3.5 sm:h-3.5" />
                  <span>Cancel</span>
                </Button>
                <Button
                  type="button"
                  size="sm"
                  onClick={async () => {
                    const isValid = await trigger(['primary_skills'])
                    if (isValid) {
                      setIsEditingSkills(false)
                      handleSubmit(onFormSubmit)()
                    }
                  }}
                  className="btn-shine text-xs h-7 sm:h-8 px-3 sm:px-4 gap-1 sm:gap-1.5 shadow-glow font-semibold bg-accent hover:bg-accent/90 text-white transition-all"
                >
                  <Check className="w-3 h-3 sm:w-3.5 sm:h-3.5" />
                  <span>Done</span>
                </Button>
              </div>
            )}
          </div>

          {/* Full-width Title and Description */}
          <div className="mt-2 sm:mt-2.5">
            <CardTitle className="text-xl sm:text-2xl font-bold tracking-tight text-text-primary font-display">
              Primary Technical Skills
            </CardTitle>
            <CardDescription className="text-xs sm:text-sm mt-1 text-zinc-400 leading-relaxed">
              The scoring algorithm calculates match scores (0–100%) by correlating these skills with public lead descriptions.
            </CardDescription>
          </div>
        </CardHeader>

        <CardContent className="p-4 sm:p-6 pt-0 sm:pt-0 space-y-5 sm:space-y-6">
          {!isEditingSkills ? (
            /* VIEW MODE: Only selected skills, ZERO suggestions */
            <div className="space-y-5 sm:space-y-6 animate-fade-in">
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <label className="text-sm font-semibold text-zinc-200 flex items-center gap-1.5">
                    <Tag className="w-3.5 h-3.5 text-accent" />
                    <span>Core Skills & Technologies</span>
                  </label>
                  <span className="text-xs text-zinc-400 font-mono bg-zinc-900 px-2.5 py-1 rounded-md border border-zinc-800">
                    {currentPrimarySkills?.length || 0} active skills
                  </span>
                </div>

                {currentPrimarySkills && currentPrimarySkills.length > 0 ? (
                  <div className="flex flex-wrap items-center gap-2">
                    {currentPrimarySkills.map((skill) => (
                      <span
                        key={skill}
                        className="inline-flex items-center px-3 py-1.5 rounded-lg border border-accent/40 bg-accent/10 text-accent text-xs font-semibold shadow-sm shadow-accent/5 transition-all"
                      >
                        {skill}
                      </span>
                    ))}
                  </div>
                ) : (
                  <p className="text-xs text-zinc-500 italic">No core skills added yet.</p>
                )}
              </div>
            </div>
          ) : (
            /* EDIT MODE: Categorized SkillTagPicker with organized stack suggestions */
            <div className="space-y-6 animate-fade-in p-1">
              <Controller
                name="primary_skills"
                control={control}
                render={({ field }) => (
                  <SkillTagPicker
                    label="Core Skills & Technologies"
                    description="Languages, frameworks, databases, and AI libraries you specialize in. Matches lead descriptions with your skill vector."
                    value={field.value}
                    onChange={field.onChange}
                    categorizedSuggestions={CATEGORIZED_SKILL_SUGGESTIONS}
                    suggestionsLabel="Curated High-Intent Tech Stacks:"
                    placeholder="Type a skill (e.g. Python, Docker, LangChain) and press Enter..."
                    error={errors.primary_skills?.message}
                    maxTags={25}
                  />
                )}
              />
            </div>
          )}
        </CardContent>

        {/* Save Preferences: Only visible when this section is in edit mode */}
        {isEditingSkills && (
          <CardFooter className="flex flex-col sm:flex-row items-center justify-between border-t border-zinc-800/80 pt-4 gap-3 animate-fade-in">
            <span className="text-xs text-zinc-400">
              {isDirty ? (
                <span className="text-amber-400 font-medium flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-amber-400 animate-pulse" />
                  <span>You have unsaved changes</span>
                </span>
              ) : (
                <span className="text-zinc-500 flex items-center gap-1.5">
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                  <span>All profile preferences in sync</span>
                </span>
              )}
            </span>
            <Button
              type="submit"
              isLoading={isLoading || isSubmitting}
              disabled={!isDirty && !saveSuccess}
              leftIcon={<Save className="w-4 h-4" />}
              className="btn-shine shadow-glow hover:shadow-glow-lg w-full sm:w-auto"
            >
              Save All Preferences
            </Button>
          </CardFooter>
        )}
      </Card>

      {/* 3. Compensation & Discovery Filters */}
      <Card className={cn(
        "relative transition-all duration-300 overflow-hidden w-full min-w-0",
        isEditingSearch
          ? "border-accent/60 bg-surface/95 shadow-xl shadow-accent/10 ring-1 ring-accent/30"
          : "border-zinc-800/80 bg-surface/90 hover:border-zinc-700/80"
      )}>
        {/* Active Top Accent Glow Beam */}
        {isEditingSearch && (
          <div
            aria-hidden="true"
            className="pointer-events-none absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r from-transparent via-accent to-transparent opacity-100 animate-fade-in"
          />
        )}

        <CardHeader className="p-4 sm:p-6 pb-3 sm:pb-4">
          {/* Top Row: Eyebrow + Status on left, Actions on right */}
          <div className="flex items-center justify-between gap-2 w-full">
            <div className="flex items-center gap-2 text-accent text-xs sm:text-sm font-medium min-w-0">
              <Globe2 className="w-3.5 h-3.5 sm:w-4 sm:h-4 shrink-0" />
              <span className="font-semibold tracking-wide truncate">Search & Availability</span>
              {isEditingSearch && (
                <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[10px] font-mono font-semibold bg-accent/15 text-accent border border-accent/30 shrink-0">
                  <span className="w-1.5 h-1.5 rounded-full bg-accent animate-ping" />
                  <span>EDITING</span>
                </span>
              )}
            </div>

            {/* Edit / Done Buttons */}
            {!isEditingSearch ? (
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={() => setIsEditingSearch(true)}
                className="border-zinc-800 bg-zinc-900/80 hover:bg-zinc-800 hover:border-accent/50 hover:text-accent gap-1.5 text-xs h-7 sm:h-8 px-2.5 sm:px-3.5 shrink-0 transition-all shadow-sm"
              >
                <Pencil className="w-3 h-3 sm:w-3.5 sm:h-3.5" />
                <span>Edit</span>
              </Button>
            ) : (
              <div className="flex items-center gap-1.5 sm:gap-2 shrink-0">
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  onClick={() => setIsEditingSearch(false)}
                  className="text-xs h-7 sm:h-8 px-2 sm:px-3 text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800/60 gap-1 transition-colors"
                >
                  <X className="w-3 h-3 sm:w-3.5 sm:h-3.5" />
                  <span>Cancel</span>
                </Button>
                <Button
                  type="button"
                  size="sm"
                  onClick={async () => {
                    const isValid = await trigger(['search_status', 'min_salary_usd', 'is_remote_only', 'target_locations'])
                    if (isValid) {
                      setIsEditingSearch(false)
                      handleSubmit(onFormSubmit)()
                    }
                  }}
                  className="btn-shine text-xs h-7 sm:h-8 px-3 sm:px-4 gap-1 sm:gap-1.5 shadow-glow font-semibold bg-accent hover:bg-accent/90 text-white transition-all"
                >
                  <Check className="w-3 h-3 sm:w-3.5 sm:h-3.5" />
                  <span>Done</span>
                </Button>
              </div>
            )}
          </div>

          {/* Full-width Title and Description */}
          <div className="mt-2 sm:mt-2.5">
            <CardTitle className="text-xl sm:text-2xl font-bold tracking-tight text-text-primary font-display">
              Compensation & Search Status
            </CardTitle>
            <CardDescription className="text-xs sm:text-sm mt-1 text-zinc-400 leading-relaxed">
              Filter incoming opportunities by minimum salary floor, remote flexibility, and intent.
            </CardDescription>
          </div>
        </CardHeader>

        <CardContent className="p-4 sm:p-6 pt-0 sm:pt-0 space-y-5 sm:space-y-6">
          {!isEditingSearch ? (
            /* VIEW MODE: Only selected status card, formatted salary, remote badge, and chosen locations */
            <div className="space-y-5 sm:space-y-6 animate-fade-in">
              {/* Selected Search Status - ONLY Show Selected Card */}
              <div className="space-y-2">
                <label className="text-sm font-semibold text-zinc-200 flex items-center gap-1.5">
                  <Compass className="w-3.5 h-3.5 text-accent" />
                  <span>Current Job Search Status</span>
                </label>
                <div className="p-4 rounded-xl border border-accent/40 bg-accent/10 shadow-sm shadow-accent/10 max-w-xl flex items-center justify-between">
                  <div className="flex items-start gap-3">
                    <div className="w-10 h-10 rounded-xl bg-accent/20 border border-accent/30 flex items-center justify-center text-accent shrink-0 mt-0.5">
                      <Compass className="w-4 h-4" />
                    </div>
                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-sm font-bold text-white">
                          {selectedStatusObj.label}
                        </span>
                        <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                      </div>
                      <p className="text-xs text-zinc-400 leading-relaxed">
                        {selectedStatusObj.desc}
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Compensation & Workplace Flexibility Display Grid */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {/* Min Salary Display */}
                <div className="p-4 rounded-xl border border-zinc-800/80 bg-zinc-950/40 flex flex-col justify-between">
                  <div className="flex items-center gap-2 text-zinc-400 text-xs font-medium">
                    <DollarSign className="w-4 h-4 text-accent" />
                    <span>Minimum Annual Compensation</span>
                  </div>
                  <div className="mt-3">
                    <span className="text-2xl font-bold font-mono text-white">
                      ${(currentSalary || 0).toLocaleString()}
                    </span>
                    <span className="text-xs text-zinc-400 ml-1.5 font-medium">USD / year</span>
                  </div>
                  <p className="text-[11px] text-zinc-500 mt-1">
                    Opportunities below this baseline are deprioritized.
                  </p>
                </div>

                {/* Workplace Flexibility Display */}
                <div className="p-4 rounded-xl border border-zinc-800/80 bg-zinc-950/40 flex flex-col justify-between">
                  <div className="flex items-center gap-2 text-zinc-400 text-xs font-medium">
                    <Globe2 className="w-4 h-4 text-accent" />
                    <span>Workplace Flexibility</span>
                  </div>
                  <div className="mt-3 flex items-center gap-2">
                    <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-lg border border-emerald-500/30 bg-emerald-500/10 text-emerald-400 text-xs font-semibold">
                      <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
                      {currentRemoteOnly ? 'Remote Opportunities Only' : 'Remote & Hybrid Allowed'}
                    </span>
                  </div>
                  <p className="text-[11px] text-zinc-500 mt-1">
                    {currentRemoteOnly
                      ? 'Excluding all jobs requiring physical on-site presence'
                      : 'Open to both remote and on-site positions'}
                  </p>
                </div>
              </div>

              {/* Preferred Geographic Locations - Only selected chips, NO suggestions */}
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <label className="text-sm font-semibold text-zinc-200 flex items-center gap-1.5">
                    <MapPin className="w-3.5 h-3.5 text-accent" />
                    <span>Preferred Geographic Locations</span>
                  </label>
                  <span className="text-xs text-zinc-400 font-mono bg-zinc-900 px-2.5 py-1 rounded-md border border-zinc-800">
                    {currentLocations?.length || 0} regions
                  </span>
                </div>
                {currentLocations && currentLocations.length > 0 ? (
                  <div className="flex flex-wrap items-center gap-2">
                    {currentLocations.map((loc) => (
                      <span
                        key={loc}
                        className="inline-flex items-center px-3 py-1.5 rounded-lg border border-accent/40 bg-accent/10 text-accent text-xs font-semibold shadow-sm shadow-accent/5 transition-all"
                      >
                        {loc}
                      </span>
                    ))}
                  </div>
                ) : (
                  <p className="text-xs text-zinc-500 italic">Any location accepted.</p>
                )}
              </div>
            </div>
          ) : (
            /* EDIT MODE: Interactive search cards, salary input, toggle, location tag picker */
            <div className="space-y-6 animate-fade-in p-1">
              {/* Search Status Segmented Cards */}
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <label className="text-sm font-semibold text-zinc-200 block">
                    Candidate Availability & Search Mode
                  </label>
                  <span className="text-[11px] font-mono text-accent">
                    {selectedStatusObj.label}
                  </span>
                </div>
                <p className="text-xs text-zinc-400">
                  Controls how aggressively our discovery engine routes high-match leads to your feed.
                </p>
                <Controller
                  name="search_status"
                  control={control}
                  render={({ field }) => (
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-3 pt-1">
                      {SEARCH_STATUSES.map((status) => {
                        const isSelected = field.value === status.id
                        return (
                          <button
                            key={status.id}
                            type="button"
                            onClick={() => field.onChange(status.id)}
                            className={cn(
                              'relative p-4 rounded-xl border text-left transition-all duration-200 cursor-pointer group flex flex-col justify-between',
                              isSelected
                                ? cn(status.activeBorder, status.activeBg, 'shadow-md ring-1 ring-accent/40 text-white scale-[1.01]')
                                : 'border-zinc-800/80 bg-zinc-950/40 hover:bg-zinc-900/60 hover:border-zinc-700 text-zinc-400'
                            )}
                          >
                            <div>
                              <div className="flex items-center justify-between mb-2">
                                <span className="text-sm font-bold text-zinc-100 group-hover:text-white transition-colors">
                                  {status.label}
                                </span>
                                <span className={cn('text-[10px] font-mono px-2 py-0.5 rounded-full border font-semibold', status.badgeColor)}>
                                  {status.tag}
                                </span>
                              </div>
                              <p className="text-xs text-zinc-400 leading-relaxed">
                                {status.desc}
                              </p>
                            </div>
                            <div className="mt-3 pt-2 border-t border-white/5 flex items-center gap-1.5 text-[11px] font-mono">
                              {isSelected ? (
                                <span className="text-accent flex items-center gap-1.5 font-semibold">
                                  <span className="w-1.5 h-1.5 rounded-full bg-accent animate-ping" />
                                  Active Selection
                                </span>
                              ) : (
                                <span className="text-zinc-500 group-hover:text-zinc-400">Click to switch</span>
                              )}
                            </div>
                          </button>
                        )
                      })}
                    </div>
                  )}
                />
              </div>

              {/* Compensation & Flexibility Row */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-1">
                {/* Min Salary Input with Presets */}
                <div className="p-4 rounded-xl border border-zinc-800/80 bg-zinc-950/40 space-y-3 flex flex-col justify-between">
                  <div>
                    <div className="flex items-center justify-between">
                      <label className="text-sm font-semibold text-zinc-200 flex items-center gap-1.5">
                        <DollarSign className="w-3.5 h-3.5 text-accent" />
                        <span>Minimum Salary Floor</span>
                      </label>
                      <span className="text-xs font-mono font-bold text-accent bg-accent/10 border border-accent/20 px-2 py-0.5 rounded-md">
                        ${(watch('min_salary_usd') || 0).toLocaleString()} USD / yr
                      </span>
                    </div>
                    <p className="text-xs text-zinc-400 mt-1">
                      Opportunities below this threshold are deprioritized.
                    </p>

                    <div className="relative mt-3">
                      <span className="absolute left-3.5 top-1/2 -translate-y-1/2 text-zinc-400 font-mono text-sm">$</span>
                      <input
                        type="number"
                        step={5000}
                        min={0}
                        placeholder="120000"
                        {...register('min_salary_usd', { valueAsNumber: true })}
                        className="w-full bg-zinc-900/80 border border-zinc-800 rounded-xl pl-8 pr-4 py-2 text-sm font-mono text-zinc-100 placeholder:text-zinc-500 focus:outline-none focus:border-accent/80 focus:ring-2 focus:ring-accent/20 transition-all"
                      />
                    </div>
                  </div>

                  {/* Quick Presets */}
                  <div className="pt-2 border-t border-zinc-900">
                    <div className="flex items-center gap-1.5 mb-1.5">
                      <span className="text-[10px] uppercase font-mono text-zinc-500">Quick Presets:</span>
                    </div>
                    <div className="flex flex-wrap gap-1.5">
                      {[60000, 90000, 120000, 150000, 180000, 220000].map((amount) => (
                        <button
                          key={amount}
                          type="button"
                          onClick={() => {
                            const event = { target: { value: amount } }
                            register('min_salary_usd', { valueAsNumber: true }).onChange(event)
                          }}
                          className={cn(
                            'text-[11px] font-mono px-2.5 py-1 rounded-full border transition-all cursor-pointer select-none',
                            watch('min_salary_usd') === amount
                              ? 'border-accent/60 bg-accent/20 text-accent font-semibold shadow-sm shadow-accent/20 ring-1 ring-accent/30'
                              : 'border-zinc-800 bg-zinc-900/60 text-zinc-400 hover:border-zinc-700 hover:text-zinc-200 hover:bg-zinc-800/80'
                          )}
                        >
                          ${amount / 1000}k
                        </button>
                      ))}
                    </div>
                  </div>
                </div>

                {/* Remote Only Toggle */}
                <div className="p-4 rounded-xl border border-zinc-800/80 bg-zinc-950/40 space-y-3 flex flex-col justify-between">
                  <div>
                    <div className="flex items-center justify-between">
                      <label className="text-sm font-semibold text-zinc-200 flex items-center gap-1.5">
                        <Globe2 className="w-3.5 h-3.5 text-accent" />
                        <span>Workplace Flexibility</span>
                      </label>
                      <span className={cn(
                        "text-[10px] font-mono px-2.5 py-0.5 rounded-full font-semibold border",
                        watch('is_remote_only')
                          ? "border-emerald-500/40 bg-emerald-500/10 text-emerald-400"
                          : "border-zinc-700 bg-zinc-800 text-zinc-400"
                      )}>
                        {watch('is_remote_only') ? 'Remote Only' : 'Hybrid / Any'}
                      </span>
                    </div>
                    <p className="text-xs text-zinc-400 mt-1">
                      Specify whether you mandate 100% location independence.
                    </p>

                    <div className="p-3.5 rounded-xl border border-zinc-800/80 bg-zinc-900/60 flex items-center justify-between mt-3">
                      <div className="pr-3">
                        <span className="text-xs font-bold text-zinc-100 block">
                          Strictly Remote Opportunities
                        </span>
                        <span className="text-[11px] text-zinc-400 block mt-0.5 leading-normal">
                          Filter out all leads requiring on-site physical presence
                        </span>
                      </div>
                      <label className="relative inline-flex items-center cursor-pointer shrink-0">
                        <input
                          type="checkbox"
                          className="sr-only peer"
                          {...register('is_remote_only')}
                        />
                        <div className="w-11 h-6 bg-zinc-800 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-border after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-accent shadow-inner"></div>
                      </label>
                    </div>
                  </div>

                  <div className="pt-2 border-t border-zinc-900 text-[11px] text-zinc-500 flex items-center gap-1.5">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                    <span>{watch('is_remote_only') ? 'Only 100% remote job signals allowed' : 'Remote, hybrid, and location-flexible signals allowed'}</span>
                  </div>
                </div>
              </div>

              {/* Target Locations with suggestions */}
              <div className="pt-1">
                <Controller
                  name="target_locations"
                  control={control}
                  render={({ field }) => (
                    <SkillTagPicker
                      label="Preferred Geographic Locations"
                      description="Regions or countries you are legally authorized and prefer to work in (e.g. Remote, US, EU, Canada)"
                      value={field.value}
                      onChange={field.onChange}
                      suggestions={POPULAR_LOCATION_SUGGESTIONS}
                      suggestionsLabel="Suggested Regions:"
                      placeholder="Type location and press Enter..."
                      maxTags={8}
                    />
                  )}
                />
              </div>
            </div>
          )}
        </CardContent>

        {/* Save Preferences: Only visible when this section is in edit mode */}
        {isEditingSearch && (
          <CardFooter className="flex flex-col sm:flex-row items-center justify-between border-t border-zinc-800/80 pt-4 gap-3 animate-fade-in">
            <span className="text-xs text-zinc-400">
              {isDirty ? (
                <span className="text-amber-400 font-medium flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-amber-400 animate-pulse" />
                  <span>You have unsaved changes</span>
                </span>
              ) : (
                <span className="text-zinc-500 flex items-center gap-1.5">
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                  <span>All profile preferences in sync</span>
                </span>
              )}
            </span>
            <Button
              type="submit"
              isLoading={isLoading || isSubmitting}
              disabled={!isDirty && !saveSuccess}
              leftIcon={<Save className="w-4 h-4" />}
              className="btn-shine shadow-glow hover:shadow-glow-lg w-full sm:w-auto"
            >
              Save All Preferences
            </Button>
          </CardFooter>
        )}
      </Card>
    </form>
  )
}
