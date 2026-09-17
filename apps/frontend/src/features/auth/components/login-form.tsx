import React, { useState } from 'react'
import { Link } from '@tanstack/react-router'
import { ArrowRight, Eye, EyeOff, Lock, Mail } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'

export const LoginForm: React.FC = () => {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [rememberMe, setRememberMe] = useState(false)

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    // Logic/API hook will be connected later
  }

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-text-primary mb-1">Welcome back</h1>
        <p className="text-xs sm:text-sm text-text-secondary">
          Enter your account credentials to continue
        </p>
      </div>

      <form className="space-y-4" onSubmit={handleSubmit}>
        <div className="space-y-1">
          <label className="block text-xs font-medium text-text-secondary">Email address</label>
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
          <div className="flex items-center justify-between text-xs">
            <label className="font-medium text-text-secondary">Password</label>
            <a href="#forgot" className="text-accent hover:text-accent-hover transition-colors">
              Forgot password?
            </a>
          </div>
          <Input
            type={showPassword ? 'text' : 'password'}
            placeholder="••••••••••••"
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
          />
        </div>

        <div className="flex items-center gap-2 pt-0.5">
          <input
            type="checkbox"
            id="remember"
            checked={rememberMe}
            onChange={(e) => setRememberMe(e.target.checked)}
            className="w-4 h-4 rounded border-border bg-background text-accent focus:ring-accent accent-accent"
          />
          <label htmlFor="remember" className="text-xs text-text-secondary cursor-pointer">
            Remember this session for 30 days
          </label>
        </div>

        <Button type="submit" className="w-full mt-2" rightIcon={<ArrowRight className="w-4 h-4" />}>
          Sign In to Dashboard
        </Button>
      </form>

      <div className="mt-8 text-center text-xs text-text-secondary">
        Don't have an account yet?{' '}
        <Link to="/register" className="text-accent hover:text-accent-hover font-semibold transition-colors">
          Create free account
        </Link>
      </div>
    </div>
  )
}
