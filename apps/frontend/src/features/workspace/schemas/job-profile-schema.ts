import { z } from 'zod'

export const experienceLevelEnum = z.enum([
  'ENTRY',
  'MID',
  'SENIOR',
  'LEAD',
  'ARCHITECT',
  'EXPERT',
])

export const jobSearchStatusEnum = z.enum([
  'ACTIVELY_LOOKING',
  'OPEN_TO_OFFERS',
  'NOT_LOOKING',
])

export const jobProfileSchema = z.object({
  target_titles: z
    .array(z.string().min(2, 'Job title must be at least 2 characters'))
    .min(1, 'Please add at least one target job title (e.g. Senior Backend Engineer)'),
  primary_skills: z
    .array(z.string().min(1, 'Skill cannot be empty'))
    .min(1, 'Please add at least one primary skill (e.g. Python, React)'),
  target_locations: z.array(z.string()),
  is_remote_only: z.boolean(),
  experience_level: experienceLevelEnum,
  min_salary_usd: z
    .number()
    .min(0, 'Salary must be positive')
    .nullable(),
  search_status: jobSearchStatusEnum,
})

export type JobProfileFormData = z.infer<typeof jobProfileSchema>
