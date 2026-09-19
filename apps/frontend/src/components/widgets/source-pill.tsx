import React from 'react'
import { Globe, Terminal, Zap } from 'lucide-react'
import { cn } from '@/lib/utils'

export type LeadSourceType = 'hacker_news' | 'remotive' | 'arbeitnow' | string

export interface SourcePillProps {
  source: LeadSourceType
  className?: string
  size?: 'sm' | 'md'
}

export const SourcePill: React.FC<SourcePillProps> = ({ source, className, size = 'md' }) => {
  const normalized = source.toLowerCase()

  const getSourceConfig = (src: string) => {
    switch (src) {
      case 'hacker_news':
        return {
          label: 'Hacker News',
          icon: Terminal,
        }
      case 'remotive':
        return {
          label: 'Remotive',
          icon: Zap,
        }
      case 'arbeitnow':
        return {
          label: 'Arbeitnow',
          icon: Globe,
        }
      default:
        return {
          label: source,
          icon: Globe,
        }
    }
  }

  const config = getSourceConfig(normalized)
  const Icon = config.icon

  return (
    <span
      className={cn(
        'inline-flex items-center gap-1.5 rounded-full border border-zinc-800 bg-zinc-900/80 text-zinc-300 font-medium select-none shrink-0',
        size === 'sm' ? 'px-2 py-0.5 text-[11px]' : 'px-2.5 py-1 text-xs',
        className
      )}
    >
      <Icon className={cn('text-text-muted', size === 'sm' ? 'w-3 h-3' : 'w-3.5 h-3.5')} />
      <span>{config.label}</span>
    </span>
  )
}
