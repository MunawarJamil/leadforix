import React from 'react'
import { cn } from '@/lib/utils'

export interface ScoreGaugeProps {
  score: number // 0 to 100
  size?: 'sm' | 'md' | 'lg'
  showLabel?: boolean
  className?: string
}

export const ScoreGauge: React.FC<ScoreGaugeProps> = ({
  score,
  size = 'md',
  showLabel = false,
  className,
}) => {
  const normalizedScore = Math.max(0, Math.min(100, Math.round(score)))

  // Color grading thresholds
  const getColorClass = (val: number) => {
    if (val >= 80) return 'text-success border-success/30 bg-success-muted'
    if (val >= 50) return 'text-warning border-warning/30 bg-warning-muted'
    return 'text-error border-error/30 bg-error-muted'
  }

  const getBarColorClass = (val: number) => {
    if (val >= 80) return 'bg-success'
    if (val >= 50) return 'bg-warning'
    return 'bg-error'
  }

  const sizeStyles = {
    sm: {
      badge: 'px-1.5 py-0.5 text-[11px] font-medium whitespace-nowrap',
      barHeight: 'h-1',
      width: 'w-14 sm:w-16',
    },
    md: {
      badge: 'px-2 py-0.5 text-xs font-semibold whitespace-nowrap',
      barHeight: 'h-1.5',
      width: 'w-24',
    },
    lg: {
      badge: 'px-3 py-1.5 text-sm font-bold whitespace-nowrap',
      barHeight: 'h-2',
      width: 'w-32',
    },
  }

  return (
    <div className={cn('inline-flex flex-col items-end gap-1 shrink-0', className)}>
      <div className="flex items-center gap-1.5 whitespace-nowrap">
        <span
          className={cn(
            'inline-flex items-center rounded-md border font-mono tracking-tight whitespace-nowrap',
            getColorClass(normalizedScore),
            sizeStyles[size].badge
          )}
        >
          {normalizedScore}% Match
        </span>
        {showLabel && (
          <span className="text-[11px] text-text-muted hidden sm:inline whitespace-nowrap">
            {normalizedScore >= 80 ? 'High Intent' : normalizedScore >= 50 ? 'Moderate' : 'Low Match'}
          </span>
        )}
      </div>

      {/* Mini Progress Track */}
      <div
        className={cn(
          'rounded-full bg-surface-hover overflow-hidden border border-border/50',
          sizeStyles[size].width,
          sizeStyles[size].barHeight
        )}
      >
        <div
          className={cn('h-full transition-all duration-500 rounded-full', getBarColorClass(normalizedScore))}
          style={{ width: `${normalizedScore}%` }}
        />
      </div>
    </div>
  )
}
