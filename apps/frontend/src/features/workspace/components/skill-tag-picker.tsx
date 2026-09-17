import * as React from 'react'
import { Plus, Tag } from 'lucide-react'
import { Chip } from '@/components/ui/chip'
import { cn } from '@/lib/utils'

export interface SkillTagPickerProps {
  label?: string
  description?: string
  value: string[]
  onChange: (tags: string[]) => void
  suggestions?: string[]
  placeholder?: string
  error?: string
  maxTags?: number
  className?: string
}

export const SkillTagPicker: React.FC<SkillTagPickerProps> = ({
  label,
  description,
  value = [],
  onChange,
  suggestions = [],
  placeholder = 'Type and press Enter...',
  error,
  maxTags = 20,
  className,
}) => {
  const [inputValue, setInputValue] = React.useState('')
  const inputRef = React.useRef<HTMLInputElement>(null)

  const handleAddTag = (rawTag: string) => {
    const trimmed = rawTag.trim()
    if (!trimmed) return
    if (value.length >= maxTags) return

    // Avoid case-insensitive duplicates
    const alreadyExists = value.some(
      (item) => item.toLowerCase() === trimmed.toLowerCase()
    )
    if (!alreadyExists) {
      onChange([...value, trimmed])
    }
    setInputValue('')
  }

  const handleRemoveTag = (indexToRemove: number) => {
    onChange(value.filter((_, idx) => idx !== indexToRemove))
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' || e.key === ',') {
      e.preventDefault()
      handleAddTag(inputValue)
    } else if (e.key === 'Backspace' && !inputValue && value.length > 0) {
      handleRemoveTag(value.length - 1)
    }
  }

  return (
    <div className={cn('space-y-2', className)}>
      {label && (
        <div className="flex items-center justify-between">
          <label className="text-sm font-medium text-text-primary flex items-center gap-1.5">
            <Tag className="w-3.5 h-3.5 text-accent" />
            <span>{label}</span>
          </label>
          {maxTags && (
            <span className="text-xs text-text-muted">
              {value.length}/{maxTags}
            </span>
          )}
        </div>
      )}
      {description && (
        <p className="text-xs text-text-secondary">{description}</p>
      )}

      {/* Tags Input Container */}
      <div
        onClick={() => inputRef.current?.focus()}
        className={cn(
          'min-h-[46px] w-full rounded-lg border bg-surface px-3 py-2 text-sm',
          'flex flex-wrap items-center gap-1.5 cursor-text transition-all duration-200',
          'focus-within:border-accent focus-within:ring-2 focus-within:ring-accent/20',
          error ? 'border-error focus-within:border-error focus-within:ring-error/20' : 'border-border'
        )}
      >
        {/* Selected Chips */}
        {value.map((tag, idx) => (
          <Chip
            key={`${tag}-${idx}`}
            variant="active"
            size="sm"
            onRemove={() => handleRemoveTag(idx)}
          >
            {tag}
          </Chip>
        ))}

        {/* Dynamic Inline Input */}
        {value.length < maxTags && (
          <div className="flex items-center flex-1 min-w-[120px]">
            <input
              ref={inputRef}
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={handleKeyDown}
              onBlur={() => {
                if (inputValue.trim()) {
                  handleAddTag(inputValue)
                }
              }}
              placeholder={value.length === 0 ? placeholder : ''}
              className="w-full bg-transparent text-sm text-text-primary placeholder:text-text-muted focus:outline-none"
            />
            {inputValue.trim() && (
              <button
                type="button"
                onClick={() => handleAddTag(inputValue)}
                className="shrink-0 p-1 text-accent hover:text-accent-hover rounded-md hover:bg-surface-hover transition-colors"
                title="Add tag"
              >
                <Plus className="w-3.5 h-3.5" />
              </button>
            )}
          </div>
        )}
      </div>

      {/* Validation Error Message */}
      {error && <p className="text-xs text-error mt-1">{error}</p>}

      {/* Suggested Quick-Picks */}
      {suggestions.length > 0 && (
        <div className="pt-1">
          <p className="text-[11px] uppercase tracking-wider text-text-muted font-mono mb-1.5">
            Suggested Tech Stacks:
          </p>
          <div className="flex flex-wrap gap-1.5">
            {suggestions.map((sug) => {
              const isSelected = value.some(
                (v) => v.toLowerCase() === sug.toLowerCase()
              )
              return (
                <Chip
                  key={sug}
                  size="sm"
                  variant={isSelected ? 'active' : 'default'}
                  onClick={() => {
                    if (isSelected) {
                      const idx = value.findIndex(
                        (v) => v.toLowerCase() === sug.toLowerCase()
                      )
                      if (idx !== -1) handleRemoveTag(idx)
                    } else {
                      handleAddTag(sug)
                    }
                  }}
                  className="cursor-pointer hover:border-accent/50"
                >
                  {sug}
                </Chip>
              )
            })}
          </div>
        </div>
      )}
    </div>
  )
}
