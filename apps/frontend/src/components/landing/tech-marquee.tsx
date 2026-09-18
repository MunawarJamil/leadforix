import { TECH_TAGS } from './data'

export function TechMarquee() {
  // Duplicate the list so translateX(-50%) loops seamlessly.
  const track = [...TECH_TAGS, ...TECH_TAGS]

  return (
    <div className="relative w-full overflow-hidden mask-fade-x py-6">
      <div className="flex w-max animate-marquee gap-3 will-change-transform">
        {track.map((tag, i) => (
          <span
            key={`${tag}-${i}`}
            className="shrink-0 rounded-full border border-border bg-surface/70 px-4 py-1.5 font-mono text-xs text-text-secondary"
          >
            {tag}
          </span>
        ))}
      </div>
    </div>
  )
}