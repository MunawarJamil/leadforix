import { Plus } from 'lucide-react'
import { Section } from './section'
import { FAQ } from './data'

export function Faq() {
  return (
    <Section id="faq" className="py-10 sm:py-15 border-t border-border">
      <div className="mx-auto max-w-6xl px-6">
        <div className="mb-12">
          <p className="font-mono text-xs uppercase tracking-[0.25em] text-accent mb-3">
            — FAQ
          </p>
          <h2 className="text-title text-text-primary">
            Questions, <span className="italic font-serif text-accent">answered.</span>
          </h2>
        </div>

        <div className="divide-y divide-border rounded-xl border border-border bg-surface/50 overflow-hidden">
          {FAQ.map(({ q, a }) => (
            <details key={q} className="group">
              <summary className="flex cursor-pointer items-center justify-between gap-4 p-5 text-left hover:bg-surface-hover/50 transition-colors list-none">
                <span className="text-sm font-medium text-text-primary">{q}</span>
                <Plus className="h-4 w-4 shrink-0 text-text-muted transition-transform duration-300 group-open:rotate-45" />
              </summary>
              <div className="px-5 pb-5 -mt-1">
                <p className="text-sm text-text-secondary leading-relaxed">{a}</p>
              </div>
            </details>
          ))}
        </div>
      </div>
    </Section>
  )
}