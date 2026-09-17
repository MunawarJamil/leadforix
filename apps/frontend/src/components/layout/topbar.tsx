import React from 'react'
import { Bell, ChevronDown, Menu, Search } from 'lucide-react'
import { useTenant } from '@/lib/tenant/use-tenant'

export interface TopbarProps {
  onMobileMenuToggle: () => void
}

export const Topbar: React.FC<TopbarProps> = ({ onMobileMenuToggle }) => {
  const { currentWorkspace, availableWorkspaces, switchWorkspace } = useTenant()

  return (
    <header className="h-16 border-b border-border bg-surface px-4 sm:px-8 flex items-center justify-between sticky top-0 z-20">
      {/* Left: Mobile Toggle & Workspace Switcher */}
      <div className="flex items-center gap-3">
        <button
          type="button"
          onClick={onMobileMenuToggle}
          className="lg:hidden p-2 rounded-lg text-text-secondary hover:text-text-primary hover:bg-surface-hover transition-colors"
        >
          <Menu className="w-5 h-5" />
        </button>

        {/* Workspace Switcher */}
        <div className="relative">
          <select
            value={currentWorkspace?.id}
            onChange={(e) => switchWorkspace(e.target.value)}
            className="appearance-none pl-3 pr-8 py-1.5 rounded-lg border border-border bg-background text-xs font-semibold text-text-primary hover:border-border-strong focus:outline-none focus:border-accent cursor-pointer transition-colors"
          >
            {availableWorkspaces.map((ws) => (
              <option key={ws.id} value={ws.id} className="bg-surface text-text-primary">
                {ws.name} ({ws.tenant_type.replace('_', ' ')})
              </option>
            ))}
          </select>
          <ChevronDown className="w-3.5 h-3.5 text-text-muted absolute right-2.5 top-1/2 -translate-y-1/2 pointer-events-none" />
        </div>
      </div>

      {/* Right: Search, Notifications & User */}
      <div className="flex items-center gap-3 sm:gap-4">
        {/* Search trigger */}
        <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-lg border border-border bg-background text-xs text-text-muted w-48 hover:border-border-strong cursor-pointer transition-colors">
          <Search className="w-3.5 h-3.5" />
          <span>Search signals...</span>
          <kbd className="ml-auto text-[10px] bg-surface border border-border px-1.5 rounded font-mono">⌘K</kbd>
        </div>

        {/* Bell */}
        <button
          type="button"
          className="relative p-2 rounded-lg text-text-secondary hover:text-text-primary hover:bg-surface-hover transition-colors"
        >
          <Bell className="w-4 h-4" />
          <span className="w-1.5 h-1.5 rounded-full bg-accent absolute top-2 right-2" />
        </button>

        {/* Avatar Placeholder */}
        <div className="w-8 h-8 rounded-full bg-accent/20 border border-accent/40 flex items-center justify-center text-xs font-bold text-accent">
          MJ
        </div>
      </div>
    </header>
  )
}
