import type { TenantType } from '@/lib/tenant/tenant-config'

export interface User {
  id: string
  email: string
  role: 'OWNER' | 'ADMIN' | 'SALES_USER' | 'AGENT'
  status: 'ACTIVE' | 'SUSPENDED' | 'PENDING_VERIFICATION'
  tenant_type: TenantType
  default_workspace_id?: string
}

export interface AuthTokens {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
}
