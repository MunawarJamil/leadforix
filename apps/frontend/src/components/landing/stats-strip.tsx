import * as React from 'react'
import { STATS } from './data'
import { Section } from './section'

export function StatsStrip() {
  return (
    <Section className="border-y border-border bg-surface/40">
      <div className="mx-auto max-w-6xl px-6 py-4">
        <ul className="flex flex-wrap items-center justify-center gap-x-10 gap-y-3 text-center">
          {STATS.map((stat, i) => (
            <React.Fragment key={stat}>
              <li className="font-mono text-sm uppercase tracking-[0.18em] text-text-secondary">
                {stat}
              </li>
              {i < STATS.length - 1 && (
                <span aria-hidden className="text-accent/60 font-mono">
                  ·
                </span>
              )}
            </React.Fragment>
          ))}
        </ul>
      </div>
    </Section >
  )
}