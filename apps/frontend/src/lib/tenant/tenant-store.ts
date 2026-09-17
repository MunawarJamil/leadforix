import { create } from 'zustand'
import { tokenStore } from '@/lib/api'
import {
  TENANT_CONFIGS,
  type Permission,
  type TenantConfig,
  type TenantType,
  type WorkspaceRole,
} from './tenant-config'

export interface WorkspaceSummary {
  id: string
  name: string
  slug: string
  tenant_type: TenantType
  role: WorkspaceRole
}

interface TenantState {
  tenantType: TenantType
  config: TenantConfig
  currentWorkspace: WorkspaceSummary | null
  availableWorkspaces: WorkspaceSummary[]
  can: (permission: Permission) => boolean
  switchWorkspace: (workspaceId: string) => void
  setTenantType: (type: TenantType) => void
  setWorkspaces: (workspaces: WorkspaceSummary[]) => void
}

const DEFAULT_MOCK_WORKSPACES: WorkspaceSummary[] = [
  {
    id: 'ws-job-seeker-01',
    name: 'Personal Portfolio',
    slug: 'personal-portfolio',
    tenant_type: 'JOB_SEEKER',
    role: 'OWNER',
  },
  {
    id: 'ws-freelancer-01',
    name: 'Munawar Consulting',
    slug: 'munawar-consulting',
    tenant_type: 'FREELANCER',
    role: 'OWNER',
  },
  {
    id: 'ws-agency-01',
    name: 'Apex Growth Agency',
    slug: 'apex-growth',
    tenant_type: 'AGENCY',
    role: 'OWNER',
  },
]

const initialWorkspace = DEFAULT_MOCK_WORKSPACES[0]
const initialTenant = initialWorkspace.tenant_type

export const useTenantStore = create<TenantState>((set, get) => ({
  tenantType: initialTenant,
  config: TENANT_CONFIGS[initialTenant],
  currentWorkspace: initialWorkspace,
  availableWorkspaces: DEFAULT_MOCK_WORKSPACES,

  can: (permission: Permission) => {
    const { config, currentWorkspace } = get()
    const hasPermission = config.permissions.includes(permission)
    if (!hasPermission) return false

    if (permission === 'team:manage' || permission === 'billing:manage') {
      return currentWorkspace?.role === 'OWNER' || currentWorkspace?.role === 'ADMIN'
    }

    return true
  },

  switchWorkspace: (workspaceId: string) => {
    const { availableWorkspaces } = get()
    const workspace = availableWorkspaces.find((w) => w.id === workspaceId)
    if (workspace) {
      tokenStore.setWorkspaceId(workspace.id)
      set({
        currentWorkspace: workspace,
        tenantType: workspace.tenant_type,
        config: TENANT_CONFIGS[workspace.tenant_type],
      })
    }
  },

  setTenantType: (type: TenantType) => {
    set({
      tenantType: type,
      config: TENANT_CONFIGS[type],
    })
  },

  setWorkspaces: (workspaces: WorkspaceSummary[]) => {
    const first = workspaces[0] || null
    if (first) {
      tokenStore.setWorkspaceId(first.id)
      set({
        availableWorkspaces: workspaces,
        currentWorkspace: first,
        tenantType: first.tenant_type,
        config: TENANT_CONFIGS[first.tenant_type],
      })
    }
  },
}))
