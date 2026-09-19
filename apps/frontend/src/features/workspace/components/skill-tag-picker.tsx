import * as React from 'react'
import { Check, Plus, Sparkles, Tag, X } from 'lucide-react'
import { cn } from '@/lib/utils'

export interface SkillTagPickerProps {
  label?: string
  description?: string
  value: string[]
  onChange: (tags: string[]) => void
  suggestions?: string[]
  categorizedSuggestions?: { category: string; items: string[] }[]
  suggestionsLabel?: string
  placeholder?: string
  error?: string
  maxTags?: number
  chipVariant?: 'accent' | 'emerald'
  className?: string
}

export const SkillTagPicker: React.FC<SkillTagPickerProps> = ({
  label,
  description,
  value = [],
  onChange,
  suggestions = [],
  categorizedSuggestions,
  suggestionsLabel,
  placeholder = 'Type and press Enter...',
  error,
  maxTags = 20,
  chipVariant = 'accent',
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

  const renderSuggestionPill = (sug: string) => {
    const isSelected = value.some(
      (v) => v.toLowerCase() === sug.toLowerCase()
    )
    return (
      <button
        key={sug}
        type="button"
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
        className={cn(
          'inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium border transition-all duration-200 select-none group',
          isSelected
            ? chipVariant === 'emerald'
              ? 'border-emerald-500/50 bg-emerald-950/40 text-emerald-400 font-mono font-medium shadow-sm shadow-emerald-500/10 ring-1 ring-emerald-500/30'
              : 'border-accent/60 bg-accent/20 text-accent font-semibold shadow-sm shadow-accent/20 ring-1 ring-accent/30'
            : 'border-zinc-800/90 bg-zinc-900/60 text-zinc-400 hover:text-zinc-100 hover:border-zinc-700 hover:bg-zinc-800/80'
        )}
      >
        {isSelected ? (
          <Check className={cn("w-3 h-3 shrink-0", chipVariant === 'emerald' ? "text-emerald-400" : "text-accent")} />
        ) : (
          <Plus className="w-3 h-3 text-zinc-500 group-hover:text-zinc-300 shrink-0" />
        )}
        <span>{sug}</span>
      </button>
    )
  }

  return (
    <div className={cn('space-y-3', className)}>
      {label && (
        <div className="flex items-center justify-between">
          <label className="text-sm font-semibold text-zinc-200 flex items-center gap-1.5">
            <Tag className={cn("w-3.5 h-3.5", chipVariant === 'emerald' ? "text-emerald-400" : "text-accent")} />
            <span>{label}</span>
          </label>
          {maxTags && (
            <span className="text-[11px] font-mono px-2 py-0.5 rounded-full bg-zinc-900 border border-zinc-800 text-zinc-400">
              {value.length} / {maxTags} max
            </span>
          )}
        </div>
      )}
      {description && (
        <p className="text-xs text-zinc-400 leading-relaxed -mt-1">{description}</p>
      )}

      {/* Tags Input Container */}
      <div
        onClick={() => inputRef.current?.focus()}
        className={cn(
          'min-h-[46px] w-full rounded-xl border bg-zinc-950/70 backdrop-blur-md px-3 py-2 text-sm',
          'flex flex-wrap items-center gap-2 cursor-text transition-all duration-200',
          'border-zinc-800/80 hover:border-zinc-700',
          chipVariant === 'emerald'
            ? 'focus-within:border-emerald-500/60 focus-within:ring-2 focus-within:ring-emerald-500/20'
            : 'focus-within:border-accent/70 focus-within:ring-2 focus-within:ring-accent/20 focus-within:bg-zinc-900/50',
          'shadow-inner',
          error ? 'border-error focus-within:border-error focus-within:ring-error/20' : ''
        )}
      >
        {/* Selected Chips */}
        {value.map((tag, idx) => (
          <span
            key={`${tag}-${idx}`}
            className={cn(
              "inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg border text-xs shadow-sm transition-all animate-fade-in",
              chipVariant === 'emerald'
                ? "border-emerald-500/30 bg-emerald-950/30 text-emerald-400 font-mono font-medium shadow-emerald-500/5"
                : "border-accent/40 bg-accent/15 text-accent font-semibold shadow-accent/10"
            )}
          >
            <span>{tag}</span>
            <button
              type="button"
              onClick={(e) => {
                e.stopPropagation()
                handleRemoveTag(idx)
              }}
              className={cn(
                "rounded-md p-0.5 transition-colors ml-0.5",
                chipVariant === 'emerald'
                  ? "hover:bg-emerald-900/40 text-emerald-400/80 hover:text-white"
                  : "hover:bg-accent/25 text-accent/80 hover:text-white"
              )}
              title={`Remove ${tag}`}
            >
              <X className="w-3 h-3" />
            </button>
          </span>
        ))}

        {/* Dynamic Inline Input */}
        {value.length < maxTags && (
          <div className="flex items-center flex-1 min-w-[150px]">
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
              placeholder={value.length === 0 ? placeholder : 'Add another title / skill...'}
              className="w-full bg-transparent text-xs sm:text-sm text-zinc-100 placeholder:text-zinc-500 focus:outline-none"
            />
          </div>
        )}
      </div>

      {/* Validation Error Message */}
      {error && <p className="text-xs text-error mt-1">{error}</p>}

      {/* Categorized Suggestions if provided */}
      {categorizedSuggestions && categorizedSuggestions.length > 0 && (
        <div className="pt-2 space-y-3 rounded-xl p-3 bg-zinc-950/40 border border-zinc-900">
          <div className="flex items-center gap-1.5 text-[11px] font-mono text-zinc-400">
            <Sparkles className={cn("w-3.5 h-3.5", chipVariant === 'emerald' ? "text-emerald-400" : "text-accent")} />
            <span className="uppercase tracking-wider font-semibold">
              {suggestionsLabel || 'Recommended Stacks & Frameworks:'}
            </span>
          </div>
          <div className="space-y-2.5">
            {categorizedSuggestions.map((cat) => (
              <div key={cat.category} className="space-y-1.5">
                <span className="text-[10px] font-mono uppercase tracking-wider text-zinc-500 block">
                  {cat.category}
                </span>
                <div className="flex flex-wrap gap-1.5">
                  {cat.items.map(renderSuggestionPill)}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Flat Suggested Quick-Picks if no categories */}
      {!categorizedSuggestions && suggestions.length > 0 && (
        <div className="pt-1.5">
          <div className="flex items-center gap-1.5 text-[11px] font-mono text-zinc-400 mb-2">
            <Sparkles className={cn("w-3 h-3", chipVariant === 'emerald' ? "text-emerald-400" : "text-accent")} />
            <span className="uppercase tracking-wider font-semibold">
              {suggestionsLabel || 'Quick Suggestions:'}
            </span>
          </div>
          <div className="flex flex-wrap gap-1.5">
            {suggestions.map(renderSuggestionPill)}
          </div>
        </div>
      )}
    </div>
  )
}

