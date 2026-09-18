import * as React from 'react'
import { motion, useReducedMotion } from 'motion/react'
import { cn } from '@/lib/utils'

export interface SectionProps extends React.HTMLAttributes<HTMLElement> {
  as?: 'section' | 'div'
  /** Delay before the reveal begins, in seconds. */
  delay?: number
  /** Distance the content travels upward on reveal, in pixels. */
  offset?: number
}

export const Section = React.forwardRef<HTMLElement, SectionProps>(
  ({ as = 'section', delay = 0, offset = 24, className, children, ...props }, ref) => {
    const prefersReduced = useReducedMotion()
    const Comp = as === 'div' ? motion.div : motion.section

    return (
      <Comp
        ref={ref as never}
        initial={prefersReduced ? false : { opacity: 0, y: offset }}
        whileInView={prefersReduced ? undefined : { opacity: 1, y: 0 }}
        viewport={{ once: true, margin: '-80px' }}
        transition={{ duration: 0.6, delay, ease: [0.22, 1, 0.36, 1] }}
        className={cn('relative w-full', className)}
         {...(props as Record<string, unknown>) }
      >
        {children}
      </Comp>
    )
  }
)
Section.displayName = 'Section'