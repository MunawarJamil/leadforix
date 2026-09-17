import { createFileRoute } from '@tanstack/react-router'
import { JobProfileForm, type JobProfileFormData } from '@/features/workspace'

export const Route = createFileRoute('/app/profile')({
  component: ProfilePage,
})

function ProfilePage() {
  const handleSaveProfile = async (data: JobProfileFormData) => {
    // Simulate API persistence
    await new Promise((resolve) => setTimeout(resolve, 800))
    console.info('Job Profile preferences saved:', data)
  }

  return (
    <div className="py-2">
      <JobProfileForm onSubmit={handleSaveProfile} />
    </div>
  )
}
