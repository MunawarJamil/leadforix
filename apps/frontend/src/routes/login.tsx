import { createFileRoute } from '@tanstack/react-router'
import { AuthLayout } from '@/components/layout/auth-layout'
import { LoginForm } from '@/features/auth/components/login-form'

export const Route = createFileRoute('/login')({
  component: () => (
    <AuthLayout
      headline="Automate high-intent discovery."
      subheadline="Log in to review real-time hiring leads from Hacker News, Remotive, and Arbeitnow matched to your skill profile."
    >
      <LoginForm />
    </AuthLayout>
  ),
})
