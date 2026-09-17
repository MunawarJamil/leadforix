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
  showLabel = true,
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
      badge: 'px-2 py-0.5 text-xs',
      barHeight: 'h-1',
      width: 'w-16',
    },
    md: {
      badge: 'px-2.5 py-1 text-xs font-semibold',
      barHeight: 'h-1.5',
      width: 'w-24',
    },
    lg: {
      badge: 'px-3 py-1.5 text-sm font-bold',
      barHeight: 'h-2',
      width: 'w-32',
    },
  }

  return (
    <div className={cn('inline-flex flex-col gap-1', className)}>
      <div className="flex items-center justify-between gap-2">
        <span
          className={cn(
            'inline-flex items-center rounded-md border font-mono tracking-tight',
            getColorClass(normalizedScore),
            sizeStyles[size].badge
          )}
        >
          {normalizedScore}% Match
        </span>
        {showLabel && (
          <span className="text-[11px] text-text-muted hidden sm:inline">
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
