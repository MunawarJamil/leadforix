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
          styles: 'border-orange-500/30 bg-orange-500/10 text-orange-400',
        }
      case 'remotive':
        return {
          label: 'Remotive',
          icon: Zap,
          styles: 'border-accent/30 bg-accent-muted text-accent',
        }
      case 'arbeitnow':
        return {
          label: 'Arbeitnow',
          icon: Globe,
          styles: 'border-cyan-500/30 bg-cyan-500/10 text-cyan-400',
        }
      default:
        return {
          label: source,
          icon: Globe,
          styles: 'border-border bg-surface text-text-secondary',
        }
    }
  }

  const config = getSourceConfig(normalized)
  const Icon = config.icon

  return (
    <span
      className={cn(
        'inline-flex items-center gap-1.5 rounded-full border font-medium select-none',
        config.styles,
        size === 'sm' ? 'px-2 py-0.5 text-[11px]' : 'px-2.5 py-1 text-xs',
        className
      )}
    >
      <Icon className={size === 'sm' ? 'w-3 h-3' : 'w-3.5 h-3.5'} />
      <span>{config.label}</span>
    </span>
  )
}
