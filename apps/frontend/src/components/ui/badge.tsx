import { cva, type VariantProps } from 'class-variance-authority'
import * as React from 'react'
import { cn } from '@/lib/utils'

export const badgeVariants = cva(
  'inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2',
  {
    variants: {
      variant: {
        default: 'border-transparent bg-accent text-white shadow hover:bg-accent-hover',
        secondary: 'border-border bg-surface text-text-secondary hover:bg-surface-hover',
        outline: 'border-border text-text-primary bg-transparent',
        success: 'border-success/20 bg-success-muted text-success',
        warning: 'border-warning/20 bg-warning-muted text-warning',
        error: 'border-error/20 bg-error-muted text-error',
        info: 'border-info/20 bg-info-muted text-info',
        accent: 'border-accent/30 bg-accent-muted text-accent',
      },
      size: {
        default: 'px-2.5 py-0.5 text-xs',
        sm: 'px-2 py-0.2 text-[11px]',
        lg: 'px-3 py-1 text-sm',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'default',
    },
  }
)

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

export function Badge({ className, variant, size, ...props }: BadgeProps) {
  return <div className={cn(badgeVariants({ variant, size }), className)} {...props} />
}
