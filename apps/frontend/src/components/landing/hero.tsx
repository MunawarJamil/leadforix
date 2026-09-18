import { Link } from '@tanstack/react-router'
import { motion, useReducedMotion, type Variants } from 'motion/react'
import { ArrowRight, Sparkles, Upload } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { HERO } from './data'
import { PreviewCards } from './preview-cards'

const container: Variants = {
  hidden: {},
  show: {
    transition: { staggerChildren: 0.08, delayChildren: 0.1 },
  },
}

const item: Variants = {
  hidden: { opacity: 0, y: 16 },
  show: { opacity: 1, y: 0, transition: { duration: 0.55, ease: [0.22, 1, 0.36, 1] } },
}

export function Hero() {
  const prefersReduced = useReducedMotion()

  return (
    <section className="relative isolate overflow-hidden">
      {/* Background: dot grid + drifting indigo glow */}
      <div className="pointer-events-none absolute inset-0 -z-10 bg-dots" aria-hidden />
      <div
        aria-hidden
        className="pointer-events-none absolute -top-40 left-1/2 -z-10 h-[520px] w-[820px] -translate-x-1/2 rounded-full opacity-40 blur-3xl animate-drift"
        style={{
          background:
            'radial-gradient(closest-side, rgb(var(--accent) / 0.55), rgb(var(--accent-alt) / 0.25), transparent 70%)',
        }}
      />

      <div className="mx-auto max-w-6xl px-6 pt-20 pb-24 sm:pt-28 sm:pb-32">
        <motion.div
          variants={prefersReduced ? undefined : container}
          initial={prefersReduced ? false : 'hidden'}
          animate={prefersReduced ? undefined : 'show'}
          className="grid grid-cols-1 lg:grid-cols-[1.05fr_0.95fr] gap-10 lg:gap-10 items-center"
        >
          {/* Left: copy */}
          <div className="flex flex-col items-start text-left">
            <motion.div variants={prefersReduced ? undefined : item}>
              <Badge
                variant="accent"
                size="lg"
                className="gap-1.5 font-mono uppercase tracking-wider"
              >
                <Sparkles className="w-3.5 h-3.5" />
                {HERO.badge}
              </Badge>
            </motion.div>

            <motion.h1
              variants={prefersReduced ? undefined : item}
              className="mt-6 text-display text-text-primary"
            >
              {HERO.headlineLead}{' '}
              <span
                className="italic font-serif bg-gradient-text bg-[length:200%_100%] bg-clip-text text-transparent animate-shimmer"
                style={{ WebkitBackgroundClip: 'text' }}
              >
                {HERO.headlineGradient}
              </span>
            </motion.h1>

            <motion.p
              variants={prefersReduced ? undefined : item}
              className="mt-6 max-w-xl text-base sm:text-lg text-text-secondary leading-relaxed"
            >
              {HERO.subtext}
            </motion.p>

            <motion.div
              variants={prefersReduced ? undefined : item}
              className="mt-9 flex flex-wrap items-center gap-3"
            >
              <Button
                asChild
                size="lg"
                className="btn-shine shadow-glow hover:shadow-glow-lg group"
              >
                <Link to="/register">
                  {HERO.ctaPrimary}
                  <ArrowRight className="ml-2 w-4 h-4 transition-transform duration-300 group-hover:translate-x-0.5" />
                </Link>
              </Button>

              <Button asChild variant="secondary" size="lg" className="relative overflow-hidden">
                <Link to="/login">{HERO.ctaSecondary}</Link>
              </Button>

              {/* Tertiary: resume upload, not yet available */}
              <button
                type="button"
                disabled
                aria-disabled="true"
                className="group inline-flex items-center gap-2 rounded-lg px-3 py-2 text-sm text-text-secondary hover:text-text-primary transition-colors disabled:opacity-60 disabled:cursor-not-allowed"
              >
                <Upload className="w-4 h-4" />
                <span>{HERO.ctaTertiary}</span>
                <span className="ml-1 inline-flex items-center rounded-full border border-border bg-surface px-2 py-0.5 text-[10px] font-mono uppercase tracking-wider text-text-muted">
                  Soon
                </span>
              </button>
            </motion.div>
          </div>

          {/* Right: floating preview cluster */}
          <motion.div variants={prefersReduced ? undefined : item} className="relative">
            <PreviewCards />
          </motion.div>
        </motion.div>
      </div>
    </section>
  )
}