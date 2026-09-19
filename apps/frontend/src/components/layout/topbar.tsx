import React from 'react'
import { Link } from '@tanstack/react-router'
import { Bell, Menu, Search, Sparkles } from 'lucide-react'

export interface TopbarProps {
  onMobileMenuToggle: () => void
}

export const Topbar: React.FC<TopbarProps> = ({ onMobileMenuToggle }) => {
  return (
    <header className="h-16 border-b border-zinc-800/80 bg-surface/90 backdrop-blur-xl px-4 sm:px-8 flex items-center justify-between sticky top-0 z-40">
      {/* Left: Mobile Drawer Toggle & Leadforix Brand Logo */}
      <div className="flex items-center gap-2.5 sm:gap-3.5 min-w-0">
        <button
          type="button"
          onClick={onMobileMenuToggle}
          className="lg:hidden p-2 -ml-1 rounded-xl text-text-secondary hover:text-text-primary hover:bg-surface-hover transition-colors shrink-0"
          aria-label="Open navigation drawer"
        >
          <Menu className="w-5 h-5" />
        </button>

        {/* Leadforix Brand Logo */}
        <Link
          to="/app/leads"
          className="flex items-center gap-2 sm:gap-2.5 outline-none group shrink-0"
        >
          <div className="relative flex h-8 w-8 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-surface to-surface-hover border border-zinc-800 group-hover:border-accent/60 shadow-xs transition-all duration-200">
            <Sparkles className="h-4 w-4 text-accent transition-transform duration-200 group-hover:scale-110 group-hover:rotate-12" />
          </div>
          <div className="flex items-center text-base sm:text-lg font-bold tracking-tight select-none">
            <span className="text-text-primary">Lead</span>
            <span className="bg-gradient-to-r from-accent via-indigo-400 to-accent-alt bg-clip-text text-transparent">
              Forix
            </span>
          </div>
        </Link>
      </div>

      {/* Right: Search, Notifications & Avatar */}
      <div className="flex items-center gap-2.5 sm:gap-4 shrink-0">
        {/* Search trigger */}
        <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-xl border border-zinc-800 bg-zinc-900/60 text-xs text-text-muted w-44 lg:w-48 hover:border-zinc-700 transition-colors">
          <Search className="w-3.5 h-3.5" />
          <span>Search signals...</span>
          <kbd className="ml-auto text-[10px] bg-zinc-800 border border-zinc-700 px-1.5 rounded font-mono text-text-muted">⌘K</kbd>
        </div>

        {/* Bell Notifications */}
        <button
          type="button"
          className="relative p-2 rounded-xl text-text-secondary hover:text-text-primary hover:bg-surface-hover transition-colors"
          aria-label="Notifications"
        >
          <Bell className="w-4 h-4" />
          <span className="w-1.5 h-1.5 rounded-full bg-accent absolute top-2 right-2 ring-2 ring-surface" />
        </button>

        {/* User Avatar */}
        <div
          className="w-8 h-8 rounded-full bg-gradient-to-br from-accent/30 to-accent/10 border border-accent/40 flex items-center justify-center text-xs font-bold text-accent shrink-0 select-none shadow-xs"
          title="Munawar Minhas"
        >
          MM
        </div>
      </div>
    </header>
  )
}
