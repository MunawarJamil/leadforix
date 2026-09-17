import * as React from 'react'
import { cn } from '@/lib/utils'

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  error?: string
  leftIcon?: React.ReactNode
  rightIcon?: React.ReactNode
  helperText?: string
}

export const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, type, error, leftIcon, rightIcon, helperText, disabled, ...props }, ref) => {
    return (
      <div className="w-full space-y-1.5">
        <div className="relative flex items-center">
          {leftIcon && (
            <div className="absolute left-3.5 text-text-muted pointer-events-none flex items-center justify-center">
              {leftIcon}
            </div>
          )}
          <input
            type={type}
            className={cn(
              'flex h-10 w-full rounded-lg border border-border bg-background px-3.5 py-2 text-sm text-text-primary placeholder:text-text-muted transition-colors file:border-0 file:bg-transparent file:text-sm file:font-medium focus-visible:outline-none focus-visible:border-accent focus-visible:ring-1 focus-visible:ring-accent disabled:cursor-not-allowed disabled:opacity-50',
              leftIcon && 'pl-10',
              rightIcon && 'pr-10',
              error && 'border-error focus-visible:border-error focus-visible:ring-error',
              className
            )}
            ref={ref}
            disabled={disabled}
            {...props}
          />
          {rightIcon && (
            <div className="absolute right-3 flex items-center justify-center text-text-muted">
              {rightIcon}
            </div>
          )}
        </div>
        {error ? (
          <p className="text-xs text-error font-medium">{error}</p>
        ) : helperText ? (
          <p className="text-xs text-text-muted">{helperText}</p>
        ) : null}
      </div>
    )
  }
)

Input.displayName = 'Input'
