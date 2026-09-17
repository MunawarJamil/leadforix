import { createRootRoute, Outlet, useNavigate } from '@tanstack/react-router'
import { useEffect } from 'react'
import { onAuthFailure } from '@/lib/api'

export const Route = createRootRoute({
  component: RootComponent,
})

function RootComponent() {
  const navigate = useNavigate()

  useEffect(() => {
    const unsubscribe = onAuthFailure(() => {
      navigate({ to: '/login' })
    })
    return unsubscribe
  }, [navigate])

  return (
    <div className="min-h-screen bg-background text-text-primary antialiased font-sans flex flex-col selection:bg-accent/20 selection:text-accent">
      <Outlet />
    </div>
  )
}
