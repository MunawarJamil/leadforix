import React from 'react'
import { Link, useRouterState } from '@tanstack/react-router'
import { Sparkles } from 'lucide-react'
import { useTenant } from '@/lib/tenant/use-tenant'
import { cn } from '@/lib/utils'

export const Sidebar: React.FC<{ className?: string }> = ({ className }) => {
  const { config, currentWorkspace } = useTenant()
  const router = useRouterState()
  const currentPath = router.location.pathname

  return (
    <aside
      className={cn(
        'w-64 border-r border-border bg-surface flex flex-col justify-between h-screen sticky top-0 select-none',
        className
      )}
    >
      {/* Brand Header */}
      <div>
        <div className="h-16 flex items-center gap-2.5 px-6 border-b border-border">
          <div className="w-8 h-8 rounded-lg bg-accent flex items-center justify-center text-white shadow-md shadow-accent/30">
            <Sparkles className="w-4 h-4" />
          </div>
          <div>
            <span className="font-bold text-base tracking-tight text-text-primary">Leadforix</span>
            <span className="block text-[10px] uppercase font-mono text-accent font-semibold tracking-wider">
              {config.label}
            </span>
          </div>
        </div>

        {/* Dynamic Nav Items */}
        <nav className="p-4 space-y-1.5">
          {config.navItems.map((item) => {
            const Icon = item.icon
            const isActive = currentPath === item.href

            return (
              <Link
                key={item.href}
                to={item.href}
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
                {item.badge && (
                  <span
                    className={cn(
                      'text-[10px] font-semibold px-2 py-0.5 rounded-full uppercase tracking-wider',
                      isActive ? 'bg-white/20 text-white' : 'bg-success-muted text-success border border-success/20'
                    )}
                  >
                    {item.badge}
                  </span>
                )}
              </Link>
            )
          })}
        </nav>
      </div>

      {/* Bottom Workspace Badge */}
      <div className="p-4 border-t border-border">
        <div className="p-3 rounded-lg border border-border bg-background flex items-center justify-between">
          <div className="truncate">
            <p className="text-xs font-semibold text-text-primary truncate">
              {currentWorkspace?.name}
            </p>
            <p className="text-[11px] text-text-muted capitalize">
              {currentWorkspace?.role.toLowerCase()}
            </p>
          </div>
          <span className="w-2 h-2 rounded-full bg-success animate-pulse shrink-0 ml-2" />
        </div>
      </div>
    </aside>
  )
}
