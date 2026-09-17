import React from 'react'
import { Inbox, type LucideIcon } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'

export interface EmptyStateProps {
  icon?: LucideIcon
  title: string
  description: string
  actionLabel?: string
  onAction?: () => void
  className?: string
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  icon: Icon = Inbox,
  title,
  description,
  actionLabel,
  onAction,
  className,
}) => {
  return (
    <div
      className={cn(
        'flex flex-col items-center justify-center p-8 sm:p-12 text-center rounded-xl border border-dashed border-border bg-surface/30',
        className
      )}
    >
      <div className="p-3.5 rounded-full bg-surface-hover border border-border text-text-muted mb-4">
        <Icon className="w-6 h-6 text-accent" />
      </div>

      <h3 className="text-base font-semibold text-text-primary mb-1.5">{title}</h3>
      <p className="text-xs sm:text-sm text-text-secondary max-w-sm mb-6 leading-relaxed">
        {description}
      </p>

      {actionLabel && onAction && (
        <Button onClick={onAction} variant="secondary" size="sm">
          {actionLabel}
        </Button>
      )}
    </div>
  )
}
