import { createFileRoute } from '@tanstack/react-router'
import { ArrowRight, CheckCircle2, Sparkles, Terminal } from 'lucide-react'

export const Route = createFileRoute('/')({
  component: HomeComponent,
})

function HomeComponent() {
  return (
    <main className="flex-1 flex flex-col items-center justify-center p-6 text-center max-w-4xl mx-auto">
      {/* Badge */}
      <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full border border-border bg-surface text-accent text-xs font-medium mb-8">
        <Sparkles className="w-3.5 h-3.5" />
        <span>Leadforix V1 — Job Seeker Acquisition Engine</span>
      </div>

      {/* Main Heading */}
      <h1 className="text-4xl sm:text-6xl font-bold tracking-tight text-text-primary mb-6 leading-tight">
        High-Intent Job Signals <br />
        <span className="text-accent">Matched to Your Skills</span>
      </h1>

      {/* Subtitle */}
      <p className="text-text-secondary text-base sm:text-lg max-w-2xl mb-10 leading-relaxed">
        Real-time hiring data from Hacker News, Remotive, and Arbeitnow. Intelligently deduplicated, scored, and ready for precision outreach.
      </p>

      {/* CTA Buttons */}
      <div className="flex flex-wrap items-center justify-center gap-4 mb-16">
        <a
          href="/register"
          className="inline-flex items-center gap-2 px-6 py-3 rounded-lg bg-accent text-white font-medium hover:bg-accent-hover transition-colors shadow-lg shadow-accent/20"
        >
          Create Free Profile
          <ArrowRight className="w-4 h-4" />
        </a>
        <a
          href="/login"
          className="inline-flex items-center gap-2 px-6 py-3 rounded-lg border border-border bg-surface hover:bg-surface-hover text-text-primary font-medium transition-colors"
        >
          Sign In
        </a>
      </div>

      {/* System Status Indicators */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 w-full max-w-2xl text-left">
        <div className="p-4 rounded-lg border border-border bg-surface">
          <div className="flex items-center gap-2 text-xs text-text-secondary mb-1">
            <CheckCircle2 className="w-3.5 h-3.5 text-success" />
            <span>Multi-Source Ingestion</span>
          </div>
          <p className="text-sm font-medium text-text-primary">HN, Remotive, Arbeitnow</p>
        </div>

        <div className="p-4 rounded-lg border border-border bg-surface">
          <div className="flex items-center gap-2 text-xs text-text-secondary mb-1">
            <CheckCircle2 className="w-3.5 h-3.5 text-success" />
            <span>Fuzzy Deduplication</span>
          </div>
          <p className="text-sm font-medium text-text-primary">Trigram Jaccard Engine</p>
        </div>

        <div className="p-4 rounded-lg border border-border bg-surface">
          <div className="flex items-center gap-2 text-xs text-text-secondary mb-1">
            <Terminal className="w-3.5 h-3.5 text-accent" />
            <span>Decoupled Gateway</span>
          </div>
          <p className="text-sm font-medium text-text-primary">Traefik v3.5 Routing</p>
        </div>
      </div>
    </main>
  )
}
