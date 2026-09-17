import React from 'react'
import { Badge, type BadgeProps } from '@/components/ui/badge'

export type StatusType =
  | 'NEW'
  | 'QUALIFIED'
  | 'DISQUALIFIED'
  | 'CONTACTED'
  | 'ARCHIVED'
  | 'ACTIVE'
  | 'CASUAL'
  | 'NOT_LOOKING'
  | string

export interface StatusBadgeProps {
  status: StatusType
  className?: string
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, className }) => {
  const normalized = status.toUpperCase()

  const getBadgeConfig = (s: string): { label: string; variant: BadgeProps['variant'] } => {
    switch (s) {
      case 'QUALIFIED':
        return { label: 'Qualified', variant: 'success' }
      case 'NEW':
        return { label: 'New Signal', variant: 'accent' }
      case 'CONTACTED':
        return { label: 'Contacted', variant: 'info' }
      case 'DISQUALIFIED':
        return { label: 'Disqualified', variant: 'error' }
      case 'ARCHIVED':
        return { label: 'Archived', variant: 'secondary' }
      case 'ACTIVE':
        return { label: 'Actively Looking', variant: 'success' }
      case 'CASUAL':
        return { label: 'Open to Offers', variant: 'warning' }
      case 'NOT_LOOKING':
        return { label: 'Not Looking', variant: 'secondary' }
      default:
        return { label: status, variant: 'secondary' }
    }
  }

  const { label, variant } = getBadgeConfig(normalized)

  return (
    <Badge variant={variant} className={className}>
      {label}
    </Badge>
  )
}
