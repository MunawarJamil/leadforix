import { createFileRoute } from '@tanstack/react-router'
import { Hero } from '@/components/landing/hero'
import { TechMarquee } from '@/components/landing/tech-marquee'
import { HowItWorks } from '@/components/landing/how-it-works'
import { LiveDemo } from '@/components/landing/live-demo'
import { Audience } from '@/components/landing/audience'
import { Faq } from '@/components/landing/faq'
import { FinalCta } from '@/components/landing/final-cta'
import { StatsStrip } from '@/components/landing/stats-strip'

export const Route = createFileRoute('/')({
  component: HomeComponent,
})

function HomeComponent() {
  return (
    <main className="flex flex-1 flex-col">
      <Hero />
      <StatsStrip />
      <TechMarquee />
      <HowItWorks />
      <LiveDemo />
      <Audience />
      <Faq />
      <FinalCta />
    </main>
  )
}