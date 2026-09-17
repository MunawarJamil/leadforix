import { cva, type VariantProps } from 'class-variance-authority'
import { X } from 'lucide-react'
import * as React from 'react'
import { cn } from '@/lib/utils'

export const chipVariants = cva(
  'inline-flex items-center gap-1.5 rounded-lg border font-medium transition-all select-none',
  {
    variants: {
      variant: {
        default: 'border-border bg-surface text-text-secondary hover:border-border-strong hover:text-text-primary',
        active: 'border-accent/40 bg-accent/15 text-accent font-semibold',
        matched: 'border-success/30 bg-success-muted text-success font-semibold',
      },
      size: {
        sm: 'px-2 py-0.5 text-xs',
        default: 'px-3 py-1 text-xs',
        lg: 'px-3.5 py-1.5 text-sm',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'default',
    },
  }
)

export interface ChipProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof chipVariants> {
  selected?: boolean
  matched?: boolean
  onRemove?: () => void
  leftIcon?: React.ReactNode
}

export const Chip = React.forwardRef<HTMLDivElement, ChipProps>(
  ({ className, variant, size, selected, matched, onRemove, leftIcon, children, onClick, ...props }, ref) => {
    const computedVariant = matched ? 'matched' : selected ? 'active' : variant

    return (
      <div
        ref={ref}
        onClick={onClick}
        className={cn(
          chipVariants({ variant: computedVariant, size }),
          onClick && 'cursor-pointer active:scale-95',
          className
        )}
        {...props}
      >
        {leftIcon && <span className="inline-flex items-center">{leftIcon}</span>}
        <span>{children}</span>
        {onRemove && (
          <button
            type="button"
            onClick={(e) => {
              e.stopPropagation()
              onRemove()
            }}
            className="rounded-full p-0.5 hover:bg-white/10 text-text-muted hover:text-text-primary transition-colors ml-0.5"
          >
            <X className="w-3 h-3" />
          </button>
        )}
      </div>
    )
  }
)

Chip.displayName = 'Chip'
