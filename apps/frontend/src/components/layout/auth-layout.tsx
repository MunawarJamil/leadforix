import React from 'react'
import { Sparkles } from 'lucide-react'

export interface AuthLayoutProps {
  children: React.ReactNode
  headline: string
  subheadline: string
}

export const AuthLayout: React.FC<AuthLayoutProps> = ({
  children,
  headline,
  subheadline,
}) => {
  return (
    <div className="min-h-screen flex items-center justify-center p-4 sm:p-8 bg-background relative overflow-hidden">
      {/* Ambient Glow */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-accent/10 rounded-full blur-3xl pointer-events-none" />

      <div className="w-full max-w-md sm:max-w-4xl grid grid-cols-1 sm:grid-cols-2 rounded-2xl border border-border bg-surface shadow-2xl overflow-hidden relative z-10">
        {/* Left: Branding Showcase (Desktop only) */}
        <div className="hidden sm:flex flex-col justify-between p-8 sm:p-10 border-r border-border bg-gradient-to-b from-surface to-background">
          <div>
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-border bg-surface-hover text-accent text-xs font-medium mb-6">
              <Sparkles className="w-3.5 h-3.5" />
              <span>Leadforix Platform</span>
            </div>
            <h2 className="text-2xl sm:text-3xl font-bold tracking-tight text-text-primary mb-3">
              {headline}
            </h2>
            <p className="text-sm text-text-secondary leading-relaxed">
              {subheadline}
            </p>
          </div>

          <div className="p-4 rounded-xl border border-border bg-surface/50">
            <div className="flex items-center gap-2 text-xs text-success font-medium mb-1">
              <span className="w-2 h-2 rounded-full bg-success animate-pulse" />
              Ingestion Pipeline Active
            </div>
            <p className="text-xs text-text-muted">
              Live Algolia HN, Remotive & Arbeitnow hiring signals.
            </p>
          </div>
        </div>

        {/* Right: Form Slot */}
        <div className="p-6 sm:p-10 flex flex-col justify-center">
          {children}
        </div>
      </div>
    </div>
  )
}
