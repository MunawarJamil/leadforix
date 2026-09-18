import { Section } from './section'
import { STEPS } from './data'

export function HowItWorks() {
  return (
    <Section className="py-10 sm:py-20">
      <div className="mx-auto max-w-6xl px-6">
        <div className="max-w-2xl mb-14">
          <p className="font-mono text-xs uppercase tracking-[0.25em] text-accent mb-3">
            — How it works
          </p>
          <h2 className="text-title text-text-primary">
            Three steps from <span className="italic font-serif text-accent">profile to outreach.</span>
          </h2>
        </div>

        <ol className="grid grid-cols-1 md:grid-cols-3 gap-6 md:gap-8">
          {STEPS.map((step, i) => (
            <li key={step.title} className="relative">
              {(() => {
                const beamGradient =
                  i === 0
                    ? 'from-transparent via-accent/80 to-transparent'
                    : i === 1
                    ? 'from-transparent via-accent-alt/80 to-transparent'
                    : 'from-transparent via-emerald-400/80 to-transparent'
                const glowColor =
                  i === 0
                    ? 'rgb(99 102 241 / 0.18)'
                    : i === 1
                    ? 'rgb(167 139 250 / 0.18)'
                    : 'rgb(16 185 129 / 0.18)'

                return (
                  <div className="group relative overflow-hidden rounded-xl border border-border bg-surface/95 backdrop-blur-sm p-6 h-full shadow-card transition-all duration-300 ease-out hover:-translate-y-1.5 hover:border-border-strong hover:shadow-glow">
                    {/* Top glowing gradient accent beam */}
                    <div
                      aria-hidden="true"
                      className={`pointer-events-none absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r ${beamGradient} opacity-70 group-hover:opacity-100 transition-opacity duration-300`}
                    />

                    {/* Subtle ambient corner backlight on hover */}
                    <div
                      aria-hidden="true"
                      className="pointer-events-none absolute -top-10 -right-10 h-32 w-32 rounded-full blur-2xl opacity-20 group-hover:opacity-50 transition-opacity duration-500"
                      style={{ background: `radial-gradient(circle, ${glowColor} 0%, transparent 70%)` }}
                    />

                    <div className="relative z-10">
                      <div className="mb-5 inline-flex h-9 w-9 items-center justify-center rounded-lg border border-accent/30 bg-accent-muted font-mono text-sm font-semibold text-accent group-hover:border-accent/60 group-hover:shadow-[0_0_12px_rgba(99,102,241,0.25)] transition-all duration-300">
                        {String(i + 1).padStart(2, '0')}
                      </div>
                      <h3 className="text-base font-semibold text-text-primary mb-2">
                        {step.title}
                      </h3>
                      <p className="text-sm text-text-secondary leading-relaxed">
                        {step.body}
                      </p>
                    </div>
                  </div>
                )
              })()}

              {/* Connector line between steps on md+ */}
              {i < STEPS.length - 1 && (
                <span
                  aria-hidden
                  className="hidden md:block absolute top-1/2 -right-4 h-px w-8 bg-gradient-to-r from-accent/50 to-transparent"
                />
              )}
            </li>
          ))}
        </ol>
      </div>
    </Section>
  )
}