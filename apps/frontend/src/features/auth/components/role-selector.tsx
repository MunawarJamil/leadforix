import React from 'react'
import { Briefcase, Building2, UserCheck } from 'lucide-react'
import type { TenantType } from '@/lib/tenant/tenant-config'
import { cn } from '@/lib/utils'

export interface RoleSelectorProps {
  value: TenantType
  onChange: (role: TenantType) => void
}

export const RoleSelector: React.FC<RoleSelectorProps> = ({ value, onChange }) => {
  const options: Array<{
    id: TenantType
    title: string
    subtitle: string
    icon: React.ComponentType<{ className?: string }>
  }> = [
    {
      id: 'JOB_SEEKER',
      title: 'Job Seeker',
      subtitle: 'Targeted tech jobs',
      icon: UserCheck,
    },
    {
      id: 'FREELANCER',
      title: 'Freelancer',
      subtitle: 'Client projects & gigs',
      icon: Briefcase,
    },
    {
      id: 'AGENCY',
      title: 'Tech Agency',
      subtitle: 'Multi-seat team pipeline',
      icon: Building2,
    },
  ]

  return (
    <div className="space-y-1.5">
      <label className="block text-xs font-medium text-text-secondary">
        I want to use Leadforix as a:
      </label>
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-2.5">
        {options.map((opt) => {
          const Icon = opt.icon
          const isSelected = value === opt.id

          return (
            <button
              key={opt.id}
              type="button"
              onClick={() => onChange(opt.id)}
              className={cn(
                'p-3 rounded-xl border text-left transition-all flex flex-col justify-between gap-2 select-none',
                isSelected
                  ? 'border-accent bg-accent/10 shadow-sm shadow-accent/20'
                  : 'border-border bg-background hover:border-border-strong hover:bg-surface-hover text-text-secondary'
              )}
            >
              <div
                className={cn(
                  'w-7 h-7 rounded-lg flex items-center justify-center',
                  isSelected ? 'bg-accent text-white' : 'bg-surface text-text-muted border border-border'
                )}
              >
                <Icon className="w-4 h-4" />
              </div>
              <div>
                <p className={cn('text-xs font-semibold', isSelected ? 'text-text-primary' : 'text-text-secondary')}>
                  {opt.title}
                </p>
                <p className="text-[10px] text-text-muted leading-tight mt-0.5">
                  {opt.subtitle}
                </p>
              </div>
            </button>
          )
        })}
      </div>
    </div>
  )
}
