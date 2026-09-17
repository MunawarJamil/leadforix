import { createFileRoute } from '@tanstack/react-router'
import { AuthLayout } from '@/components/layout/auth-layout'
import { RegisterForm } from '@/features/auth/components/register-form'

export const Route = createFileRoute('/register')({
  component: () => (
    <AuthLayout
      headline="Precision client acquisition built for builders."
      subheadline="Bypass cold mass-spam. Discover high-intent hiring companies seeking your exact tech stack with zero spam compliance risk."
    >
      <RegisterForm />
    </AuthLayout>
  ),
})
