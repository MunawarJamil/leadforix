import { Link } from '@tanstack/react-router'
import { ArrowRight } from 'lucide-react'
import { Section } from './section'
import { Button } from '@/components/ui/button'

export function FinalCta() {
  return (
    <Section className="py-20 sm:py-10">
      <div className="mx-auto max-w-6xl px-6">
        <div className="relative isolate overflow-hidden rounded-2xl border border-border bg-surface p-10 sm:p-16 text-center">
          <div
            aria-hidden
            className="pointer-events-none absolute inset-0 -z-10 opacity-60"
            style={{
              background:
                'radial-gradient(600px 300px at 50% 0%, rgb(var(--accent) / 0.35), transparent 70%)',
            }}
          />
          <h2 className="text-title text-text-primary mx-auto max-w-2xl">
            Ready to see roles that <span className="italic font-serif text-accent">actually fit?</span>
          </h2>
          <p className="mt-4 mx-auto max-w-xl text-text-secondary leading-relaxed">
            Build your profile in two minutes. Start seeing ranked leads today.
          </p>
          <div className="mt-8 flex flex-wrap items-center justify-center gap-3">
            <Button asChild size="lg" className="btn-shine shadow-glow hover:shadow-glow-lg group">
              <Link to="/register">
                Create Free Profile
                <ArrowRight className="ml-2 w-4 h-4 transition-transform duration-300 group-hover:translate-x-0.5" />
              </Link>
            </Button>
            <Button asChild variant="secondary" size="lg">
              <Link to="/login">Sign In</Link>
            </Button>
          </div>
        </div>
      </div>
    </Section>
  )
}