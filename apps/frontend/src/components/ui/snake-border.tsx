import * as React from 'react'
import { cn } from '@/lib/utils'

export interface SnakeBorderProps {
  className?: string
  /** Primary glow color for the snake's head */
  colorFrom?: string
  /** Fading trail color */
  colorTo?: string
  /** Seconds for one full lap around the card. Higher = slower. Default: 8 */
  duration?: number
  /** Length of the snake as a percentage of total card perimeter. Default: 24 */
  size?: number
  /** Border stroke width in pixels. Default: 1.5 */
  strokeWidth?: number
  /** Corner radius in pixels. Default: 12 */
  rx?: number | string
}

export function SnakeBorder({
  className,
  colorFrom = '#6366F1',
  colorTo = '#A78BFA',
  duration = 8,
  size = 24,
  strokeWidth = 1.5,
  rx = 12,
}: SnakeBorderProps) {
  const id = React.useId().replace(/:/g, '')

  return (
    <svg
      aria-hidden="true"
      className={cn(
        'pointer-events-none absolute inset-0 h-full w-full overflow-visible rounded-[inherit]',
        className
      )}
    >
      <defs>
        <linearGradient id={`snake-grad-${id}`} x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor={colorFrom} stopOpacity="1" />
          <stop offset="50%" stopColor={colorTo} stopOpacity="0.75" />
          <stop offset="100%" stopColor={colorTo} stopOpacity="0" />
        </linearGradient>
        <filter id={`snake-glow-${id}`} x="-20%" y="-20%" width="140%" height="140%">
          <feGaussianBlur stdDeviation="2.5" result="blur" />
          <feMerge>
            <feMergeNode in="blur" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
      </defs>

      {/* Slowly traveling glowing snake border */}
      <rect
        x="0.75"
        y="0.75"
        width="calc(100% - 1.5px)"
        height="calc(100% - 1.5px)"
        rx={rx}
        fill="none"
        stroke={`url(#snake-grad-${id})`}
        strokeWidth={strokeWidth}
        strokeLinecap="round"
        pathLength="100"
        strokeDasharray={`${size} ${100 - size}`}
        filter={`url(#snake-glow-${id})`}
        style={{
          animation: `snake-move ${duration}s linear infinite`,
        }}
      />
    </svg>
  )
}
