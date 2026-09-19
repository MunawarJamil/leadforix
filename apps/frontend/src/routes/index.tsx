import { createFileRoute } from '@tanstack/react-router'
import { Navbar } from '@/components/landing/navbar'
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
    <div className="relative min-h-screen flex flex-col bg-background text-text-primary selection:bg-accent/30 selection:text-white w-full max-w-full overflow-x-clip">
      <Navbar />
      <main className="flex flex-1 flex-col w-full max-w-full overflow-x-clip">
        <Hero />
        <StatsStrip />
        <TechMarquee />
        <HowItWorks />
        <LiveDemo />
        <Audience />
        <Faq />
        <FinalCta />
      </main>
    </div>
  )
}
