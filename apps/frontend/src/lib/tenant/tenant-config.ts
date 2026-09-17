import {
  Briefcase,
  CreditCard,
  FileText,
  Layers,
  LayoutDashboard,
  Mail,
  Search,
  Settings,
  Sparkles,
  Users,
  type LucideIcon,
} from 'lucide-react'

export type TenantType = 'JOB_SEEKER' | 'FREELANCER' | 'AGENCY'
export type WorkspaceRole = 'OWNER' | 'ADMIN' | 'MEMBER'

export type Permission =
  | 'leads:view'
  | 'leads:discover'
  | 'profile:manage'
  | 'campaigns:manage'
  | 'agents:manage'
  | 'research:view'
  | 'knowledge:manage'
  | 'team:manage'
  | 'billing:manage'

export interface NavItem {
  title: string
  href: string
  icon: LucideIcon
  badge?: string
  permission?: Permission
}

export interface TenantConfig {
  name: string
  label: string
  description: string
  navItems: NavItem[]
  dashboardWidgets: string[]
  permissions: Permission[]
}

export const TENANT_CONFIGS: Record<TenantType, TenantConfig> = {
  JOB_SEEKER: {
    name: 'JOB_SEEKER',
    label: 'Job Seeker',
    description: 'Direct skill-matched opportunity discovery and outreach',
    navItems: [
      { title: 'Dashboard', href: '/app/dashboard', icon: LayoutDashboard },
      { title: 'Matched Leads', href: '/app/leads', icon: Sparkles, badge: 'Live' },
      { title: 'Job Profile', href: '/app/profile', icon: FileText },
      { title: 'Outreach & Applies', href: '/app/outreach', icon: Mail },
      { title: 'Settings', href: '/app/settings', icon: Settings },
    ],
    dashboardWidgets: ['stat-overview', 'lead-feed', 'skill-readiness'],
    permissions: ['leads:view', 'leads:discover', 'profile:manage'],
  },

  FREELANCER: {
    name: 'FREELANCER',
    label: 'Freelancer',
    description: 'High-intent client discovery, proposal pipeline, and outreach',
    navItems: [
      { title: 'Dashboard', href: '/app/dashboard', icon: LayoutDashboard },
      { title: 'Client Opportunities', href: '/app/leads', icon: Sparkles, badge: 'Live' },
      { title: 'Service Profile', href: '/app/profile', icon: FileText },
      { title: 'Campaigns', href: '/app/campaigns', icon: Layers },
      { title: 'Outreach', href: '/app/outreach', icon: Mail },
      { title: 'Settings', href: '/app/settings', icon: Settings },
    ],
    dashboardWidgets: ['stat-overview', 'lead-feed', 'campaign-pipeline'],
    permissions: ['leads:view', 'leads:discover', 'profile:manage', 'campaigns:manage'],
  },

  AGENCY: {
    name: 'AGENCY',
    label: 'Tech Agency',
    description: 'Multi-seat team pipeline, autonomous AI agents, and client outreach',
    navItems: [
      { title: 'Dashboard', href: '/app/dashboard', icon: LayoutDashboard },
      { title: 'Lead Pipeline', href: '/app/leads', icon: Sparkles, badge: 'Live' },
      { title: 'Campaigns', href: '/app/campaigns', icon: Layers },
      { title: 'AI SDR Agents', href: '/app/agents', icon: Briefcase },
      { title: 'Company Research', href: '/app/research', icon: Search },
      { title: 'Knowledge Base', href: '/app/knowledge', icon: FileText },
      { title: 'Team & Seats', href: '/app/team', icon: Users, permission: 'team:manage' },
      { title: 'Billing & Usage', href: '/app/billing', icon: CreditCard, permission: 'billing:manage' },
      { title: 'Settings', href: '/app/settings', icon: Settings },
    ],
    dashboardWidgets: ['stat-overview', 'lead-feed', 'campaign-pipeline', 'agent-status', 'team-capacity'],
    permissions: [
      'leads:view',
      'leads:discover',
      'profile:manage',
      'campaigns:manage',
      'agents:manage',
      'research:view',
      'knowledge:manage',
      'team:manage',
      'billing:manage',
    ],
  },
}
