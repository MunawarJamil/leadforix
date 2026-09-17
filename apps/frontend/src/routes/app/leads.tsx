import { createFileRoute } from '@tanstack/react-router'
import { LeadFeed, type Lead } from '@/features/leads'

export const Route = createFileRoute('/app/leads')({
  component: LeadsPage,
})

function LeadsPage() {
  const handlePrepareOutreach = (lead: Lead) => {
    console.info('Preparing AI outreach for lead:', lead.company_name, lead.title)
    alert(`AI Outreach triggered for ${lead.company_name} (${lead.title}). Autonomous workflow will be available in Phase 2!`)
  }

  return (
    <div className="py-2">
      <LeadFeed onPrepareOutreach={handlePrepareOutreach} />
    </div>
  )
}
