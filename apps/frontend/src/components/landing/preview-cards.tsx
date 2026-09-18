import { motion, useReducedMotion } from 'motion/react'
import { FloatingLeadCard } from './lead-card'
import { SAMPLE_LEADS } from './data'

/**
 * Cluster of 3 lead cards used in the hero.
 * On lg+ they stack with rotation for a "fanned deck" feel.
 * On smaller screens they collapse to a single column.
 */
export function PreviewCards() {
  const prefersReduced = useReducedMotion()
  const [a, b, c] = SAMPLE_LEADS

  return (
    <div className="relative mx-auto w-full max-w-md lg:max-w-none lg:h-[440px]">
      {/* Ambient glow behind the cluster */}
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0 -z-10 rounded-full opacity-50 blur-3xl"
        style={{
          background:
            'radial-gradient(closest-side, rgb(var(--accent) / 0.35), transparent 70%)',
        }}
      />

      <div className="flex flex-col gap-4 lg:block">
        {[a, b, c].map((lead, i) => {
          const layout =
            i === 0
              ? 'lg:absolute lg:top-0 lg:left-0 lg:z-20 lg:-rotate-3'
              : i === 1
              ? 'lg:absolute lg:top-20 lg:right-0 lg:z-10 lg:rotate-2'
              : 'lg:absolute lg:bottom-0 lg:left-6 lg:z-30 lg:-rotate-1'

          return (
            <motion.div
              key={lead.id}
              initial={prefersReduced ? false : { opacity: 0, y: 20 }}
              animate={prefersReduced ? undefined : { opacity: 1, y: 0 }}
              transition={{
                duration: 0.6,
                delay: 0.25 + i * 0.12,
                ease: [0.22, 1, 0.36, 1],
              }}
              className={layout}
              style={{ animationDelay: `${i * 1.2}s` }}
            >
              <FloatingLeadCard lead={lead} scoreDelay={0.4 + i * 0.15} />
            </motion.div>
          )
        })}
      </div>
    </div>
  )
}