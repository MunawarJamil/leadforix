import React from 'react'
import { Card, CardContent } from '@/components/ui/card'
import { cn } from '@/lib/utils'

export interface StatCardProps {
  title: string
  value: string | number
  description?: string
  trend?: {
    value: string
    positive?: boolean
  }
  icon?: React.ReactNode
  className?: string
}

export const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  description,
  trend,
  icon,
  className,
}) => {
  return (
    <Card className={cn('relative overflow-hidden bg-surface hover:border-border-strong transition-all', className)}>
      <CardContent className="p-5 flex flex-col justify-between h-full">
        <div className="flex items-center justify-between gap-2 mb-3">
          <span className="text-xs font-medium text-text-secondary uppercase tracking-wider">
            {title}
          </span>
          {icon && (
            <div className="p-2 rounded-lg bg-surface-hover text-accent border border-border">
              {icon}
            </div>
          )}
        </div>

        <div>
          <div className="text-2xl sm:text-3xl font-bold tracking-tight text-text-primary mb-1 font-mono">
            {value}
          </div>

          <div className="flex items-center gap-2 text-xs">
            {trend && (
              <span
                className={cn(
                  'font-medium px-1.5 py-0.5 rounded',
                  trend.positive
                    ? 'text-success bg-success-muted'
                    : 'text-error bg-error-muted'
                )}
              >
                {trend.value}
              </span>
            )}
            {description && (
              <span className="text-text-muted truncate">{description}</span>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
