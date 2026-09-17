import React, { useState } from 'react'
import { Sidebar } from './sidebar'
import { Topbar } from './topbar'
import { MobileNav } from './mobile-nav'

export const AppShell: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [mobileNavOpen, setMobileNavOpen] = useState(false)

  return (
    <div className="min-h-screen flex bg-background text-text-primary">
      {/* Desktop Sidebar */}
      <Sidebar className="hidden lg:flex shrink-0" />

      {/* Mobile Drawer */}
      <MobileNav isOpen={mobileNavOpen} onClose={() => setMobileNavOpen(false)} />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0">
        <Topbar onMobileMenuToggle={() => setMobileNavOpen(true)} />
        <main className="flex-1 p-4 sm:p-8 max-w-7xl w-full mx-auto">
          {children}
        </main>
      </div>
    </div>
  )
}
