import React, { useState } from 'react'
import { Link } from '@tanstack/react-router'
import { ArrowRight, Eye, EyeOff, Lock, Mail } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { RoleSelector } from './role-selector'
import type { TenantType } from '@/lib/tenant/tenant-config'

export const RegisterForm: React.FC = () => {
  const [role, setRole] = useState<TenantType>('JOB_SEEKER')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    // Logic/API hook will be connected later
  }

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-text-primary mb-1">Create an account</h1>
        <p className="text-xs sm:text-sm text-text-secondary">
          Set up your profile and automated workspace
        </p>
      </div>

      <form className="space-y-4" onSubmit={handleSubmit}>
        <RoleSelector value={role} onChange={setRole} />

        <div className="space-y-1">
          <label className="block text-xs font-medium text-text-secondary">Work Email</label>
          <Input
            type="email"
            placeholder="alex@company.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            leftIcon={<Mail className="w-4 h-4" />}
            required
          />
        </div>

        <div className="space-y-1">
          <label className="block text-xs font-medium text-text-secondary">Password</label>
          <Input
            type={showPassword ? 'text' : 'password'}
            placeholder="At least 8 characters..."
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            leftIcon={<Lock className="w-4 h-4" />}
            rightIcon={
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="hover:text-text-primary transition-colors"
              >
                {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            }
            required
            helperText="Must contain 8+ characters with uppercase, number & symbol."
          />
        </div>

        <Button type="submit" className="w-full mt-2" rightIcon={<ArrowRight className="w-4 h-4" />}>
          Create Workspace & Continue
        </Button>
      </form>

      <div className="mt-8 text-center text-xs text-text-secondary">
        Already have an account?{' '}
        <Link to="/login" className="text-accent hover:text-accent-hover font-semibold transition-colors">
          Sign In
        </Link>
      </div>
    </div>
  )
}
