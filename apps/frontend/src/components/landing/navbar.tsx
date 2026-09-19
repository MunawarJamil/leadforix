import * as React from 'react'
import { Link } from '@tanstack/react-router'
import { motion, AnimatePresence } from 'motion/react'
import { ArrowRight, Sparkles, Menu, X } from 'lucide-react'
import { Button } from '@/components/ui/button'

interface NavLinkItem {
  label: string
  href: string
}

const NAV_LINKS: NavLinkItem[] = [
  { label: 'How It Works', href: '#how-it-works' },
  { label: 'Live Signals', href: '#live-demo' },
  { label: 'Solutions', href: '#audience' },
  { label: 'FAQ', href: '#faq' },
]

export function Navbar() {
  const [mobileMenuOpen, setMobileMenuOpen] = React.useState(false)

  // Prevent background scroll when mobile navigation drawer is active
  React.useEffect(() => {
    if (mobileMenuOpen) {
      document.body.style.overflow = 'hidden'
    } else {
      document.body.style.overflow = ''
    }
    return () => {
      document.body.style.overflow = ''
    }
  }, [mobileMenuOpen])

  // Dismiss mobile drawer on Escape key
  React.useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        setMobileMenuOpen(false)
      }
    }
    if (mobileMenuOpen) {
      window.addEventListener('keydown', handleKeyDown)
    }
    return () => {
      window.removeEventListener('keydown', handleKeyDown)
    }
  }, [mobileMenuOpen])

  // Auto-close mobile drawer when window resizes to desktop breakpoint (>= 1024px)
  React.useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth >= 1024) {
        setMobileMenuOpen(false)
      }
    }
    window.addEventListener('resize', handleResize)
    return () => {
      window.removeEventListener('resize', handleResize)
    }
  }, [])

  return (
    <>
      <header className="sticky top-0 z-50 w-full max-w-full overflow-x-clip bg-background/80 backdrop-blur-xl border-b border-zinc-800/70 transition-colors">
        <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8 h-16 sm:h-20 flex items-center justify-between gap-3 sm:gap-4 w-full min-w-0">
          {/* Left: Brand / Logo */}
          <div className="flex items-center gap-2.5 sm:gap-4 shrink-0">
            <a
              href="#top"
              className="group flex items-center gap-2.5 outline-none focus-visible:ring-2 focus-visible:ring-accent rounded-lg"
            >
              {/* Logo Icon Mark */}
              <div className="relative flex h-8 w-8 sm:h-9 sm:w-9 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-surface to-surface-hover border border-border group-hover:border-accent/60 transition-all duration-300">
                <Sparkles className="h-4 w-4 text-accent transition-transform duration-300 group-hover:scale-110 group-hover:rotate-12" />
              </div>

              {/* Wordmark */}
              <div className="flex items-center text-xl sm:text-2xl font-bold tracking-tight">
                <span className="text-text-primary">Lead</span>
                <span className="bg-gradient-to-r from-accent via-indigo-400 to-accent-alt bg-clip-text text-transparent">
                  Forix
                </span>
              </div>
            </a>

            {/* Live Signals Indicator (hidden on small mobile to preserve layout) */}
            <div className="hidden md:inline-flex items-center gap-1.5 text-[8px] font-mono tracking-wider font-semibold text-emerald-400 pl-1">
              <span className="relative flex h-1.5 w-1.5">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
                <span className="relative inline-flex rounded-full h-1.5 w-1.5 bg-emerald-500" />
              </span>
              <span>LIVE SIGNALS</span>
            </div>
          </div>

          {/* Center: In-Page Navigation Links (Visible on desktop screens >= 1024px) */}
          <nav
            aria-label="Main Navigation"
            className="hidden lg:flex items-center gap-6 xl:gap-8"
          >
            {NAV_LINKS.map((item) => (
              <a
                key={item.href}
                href={item.href}
                className="text-sm font-medium text-text-secondary hover:text-text-primary transition-colors"
              >
                {item.label}
              </a>
            ))}
          </nav>

          {/* Right: Auth Action CTA Buttons */}
          <div className="flex items-center gap-2 sm:gap-3 shrink-0">
            {/* Sign In link (desktop & tablet >= 640px) */}
            <Link
              to="/login"
              className="hidden sm:inline-flex items-center text-sm font-medium text-text-secondary hover:text-text-primary transition-colors px-2 py-1.5"
            >
              Sign in
            </Link>

            {/* Primary Action Button */}
            <Button
              asChild
              size="default"
              className="btn-shine shadow-glow hover:shadow-glow-lg group h-9 px-3 text-xs sm:h-10 sm:px-4 sm:text-sm shrink-0"
            >
              <Link to="/register">
                <span className="hidden sm:inline">Get Started Free</span>
                <span className="inline sm:hidden">Get Started</span>
                <ArrowRight className="ml-1 sm:ml-1.5 w-3.5 h-3.5 sm:w-4 sm:h-4 transition-transform duration-300 group-hover:translate-x-0.5" />
              </Link>
            </Button>

            {/* Mobile / Tablet Hamburger Toggle (hidden on desktop >= 1024px) */}
            <button
              type="button"
              onClick={() => setMobileMenuOpen((prev) => !prev)}
              className="lg:hidden flex h-9 w-9 sm:h-10 sm:w-10 items-center justify-center rounded-lg border border-border bg-surface text-text-secondary hover:text-text-primary hover:border-border-strong focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent transition-colors shrink-0"
              aria-label={mobileMenuOpen ? 'Close navigation menu' : 'Open navigation menu'}
              aria-expanded={mobileMenuOpen}
              aria-controls="mobile-navigation-menu"
            >
              {mobileMenuOpen ? <X className="h-4 w-4 sm:h-5 sm:w-5" /> : <Menu className="h-4 w-4 sm:h-5 sm:w-5" />}
            </button>
          </div>
        </div>

        {/* Mobile / Tablet Drawer Navigation Menu */}
        <AnimatePresence>
          {mobileMenuOpen && (
            <motion.div
              id="mobile-navigation-menu"
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              transition={{ duration: 0.25, ease: [0.22, 1, 0.36, 1] }}
              className="lg:hidden border-b border-border/80 bg-background/95 backdrop-blur-2xl max-h-[calc(100dvh-4rem)] sm:max-h-[calc(100dvh-5rem)] overflow-y-auto"
            >
              <div className="flex flex-col gap-2 px-4 sm:px-6 pt-3 pb-6">
                {/* Mobile Live Signals Badge */}
                <div className="flex items-center gap-1.5 py-1 text-[10px] font-mono text-emerald-400">
                  <span className="relative flex h-1.5 w-1.5">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
                    <span className="relative inline-flex rounded-full h-1.5 w-1.5 bg-emerald-500" />
                  </span>
                  <span>Ingestion Active: Algolia + Remotive + Arbeitnow</span>
                </div>

                <div className="my-2 h-[1px] bg-border/60" />

                {/* Navigation Links */}
                {NAV_LINKS.map((item) => (
                  <a
                    key={item.href}
                    href={item.href}
                    onClick={() => setMobileMenuOpen(false)}
                    className="flex items-center justify-between py-2.5 px-2 rounded-lg text-sm font-medium text-text-secondary hover:text-text-primary hover:bg-surface transition-colors"
                  >
                    <span>{item.label}</span>
                    <ArrowRight className="h-3.5 w-3.5 text-text-muted" />
                  </a>
                ))}

                <div className="my-2 h-[1px] bg-border/60" />

                {/* Auth CTAs */}
                <div className="flex flex-col gap-2.5 pt-1">
                  <Link
                    to="/login"
                    onClick={() => setMobileMenuOpen(false)}
                    className="w-full text-center py-2.5 rounded-lg border border-border bg-surface hover:bg-surface-hover text-sm font-medium text-text-primary transition-colors"
                  >
                    Sign in
                  </Link>
                  <Button
                    asChild
                    size="default"
                    className="btn-shine w-full shadow-glow hover:shadow-glow-lg group"
                  >
                    <Link
                      to="/register"
                      onClick={() => setMobileMenuOpen(false)}
                    >
                      <span>Get Started Free</span>
                      <ArrowRight className="ml-1.5 w-4 h-4 transition-transform duration-300 group-hover:translate-x-0.5" />
                    </Link>
                  </Button>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </header>

      {/* Backdrop Dimmer Overlay (lg:hidden) */}
      <AnimatePresence>
        {mobileMenuOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            onClick={() => setMobileMenuOpen(false)}
            className="fixed inset-0 top-16 sm:top-20 z-40 bg-black/60 backdrop-blur-sm lg:hidden"
            aria-hidden="true"
          />
        )}
      </AnimatePresence>
    </>
  )
}
