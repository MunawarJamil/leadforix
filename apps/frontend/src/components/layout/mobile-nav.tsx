import React from 'react'
import { Link, useRouterState } from '@tanstack/react-router'
import { Sparkles, X } from 'lucide-react'
import { useTenant } from '@/lib/tenant/use-tenant'
import { cn } from '@/lib/utils'

export interface MobileNavProps {
  isOpen: boolean
  onClose: () => void
}

export const MobileNav: React.FC<MobileNavProps> = ({ isOpen, onClose }) => {
  const { config, currentWorkspace } = useTenant()
  const router = useRouterState()
  const currentPath = router.location.pathname

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 lg:hidden">
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-background/80 backdrop-blur-sm transition-opacity"
        onClick={onClose}
      />

      {/* Drawer */}
      <div className="fixed inset-y-0 left-0 w-3/4 max-w-xs bg-surface border-r border-border p-6 flex flex-col justify-between shadow-2xl animate-in slide-in-from-left duration-200">
        <div>
          <div className="flex items-center justify-between pb-6 border-b border-border mb-6">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-lg bg-accent flex items-center justify-center text-white">
                <Sparkles className="w-4 h-4" />
              </div>
              <span className="font-bold text-base text-text-primary">Leadforix</span>
            </div>
            <button
              onClick={onClose}
              className="p-1 rounded-md text-text-muted hover:text-text-primary hover:bg-surface-hover"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          <nav className="space-y-1.5">
            {config.navItems.map((item) => {
              const Icon = item.icon
              const isActive = currentPath === item.href

              return (
                <Link
                  key={item.href}
                  to={item.href}
                  onClick={onClose}
                  className={cn(
                    'flex items-center justify-between px-3.5 py-2.5 rounded-lg text-sm font-medium transition-colors',
                    isActive
                      ? 'bg-accent text-white shadow-sm shadow-accent/20'
                      : 'text-text-secondary hover:text-text-primary hover:bg-surface-hover'
                  )}
                >
                  <div className="flex items-center gap-3">
                    <Icon className={cn('w-4 h-4', isActive ? 'text-white' : 'text-text-muted')} />
                    <span>{item.title}</span>
                  </div>
                </Link>
              )
            })}
          </nav>
        </div>

        <div className="pt-4 border-t border-border text-xs text-text-muted">
          Active: <span className="text-text-primary font-medium">{currentWorkspace?.name}</span>
        </div>
      </div>
    </div>
  )
}
