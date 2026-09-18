import { Section } from './section'
import { LeadCard } from './lead-card'
import { SAMPLE_LEADS } from './data'

export function LiveDemo() {
  return (
    <Section className="py-10 sm:py-10 border-t border-border bg-surface/30">
      <div className="mx-auto max-w-6xl px-6">
        <div className="max-w-2xl mb-14">
          <p className="font-mono text-xs uppercase tracking-[0.25em] text-accent mb-3">
            — Live preview
          </p>
          <h2 className="text-title text-text-primary">
            Every role, <span className="italic font-serif text-accent">scored against your stack.</span>
          </h2>
          <p className="mt-4 text-text-secondary leading-relaxed">
            Match scores update as your profile grows. Watch the gauges fill
            the moment a lead enters your feed.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {SAMPLE_LEADS.map((lead, i) => (
            <LeadCard
              key={lead.id}
              lead={lead}
              scoreDelay={0.15 + i * 0.2}
            />
          ))}
        </div>
      </div>
    </Section>
  )
}