/** @type {import('tailwindcss').Config} */

// Colors live in index.css as space-separated RGB channels (e.g. "99 102 241").
// This helper lets Tailwind inject its own alpha, so bg-accent/20, border-accent/40,
// ring-accent/30 etc. all work from one token. No more hand-written "#6366F11A" variants.
const token = (name) => `rgb(var(--${name}) / <alpha-value>)`;

export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        background: token("background"),
        surface: {
          DEFAULT: token("surface"),
          hover: token("surface-hover"),
        },
        // Borders are always translucent white, so alpha is baked into the variable.
        border: {
          DEFAULT: "var(--border)",
          strong: "var(--border-strong)",
        },
        text: {
          primary: token("text-primary"),
          secondary: token("text-secondary"),
          muted: token("text-muted"),
        },
        accent: {
          DEFAULT: token("accent"),
          hover: token("accent-hover"),
          alt: token("accent-alt"), // violet, used only in gradients
          muted: "rgb(var(--accent) / 0.1)", // kept so existing bg-accent-muted keeps working
        },
        success: { DEFAULT: token("success"), muted: "rgb(var(--success) / 0.1)" },
        warning: { DEFAULT: token("warning"), muted: "rgb(var(--warning) / 0.1)" },
        error: { DEFAULT: token("error"), muted: "rgb(var(--error) / 0.1)" },
        info: { DEFAULT: token("info"), muted: "rgb(var(--info) / 0.1)" },
      },

      // Variable fonts are loaded via @fontsource-variable in main.tsx.
      fontFamily: {
        sans: ['"Plus Jakarta Sans"', '"Geist Variable"', "ui-sans-serif", "system-ui", "sans-serif"],
        display: ['"Playfair Display"', '"Cormorant Garamond"', "Georgia", "serif"],
        serif: ['"Playfair Display"', '"Cormorant Garamond"', "Georgia", "serif"],
        mono: ['"JetBrains Mono"', '"Geist Mono Variable"', "ui-monospace", "monospace"],
      },

      // Fluid type: scales smoothly with the viewport, tuned for high-contrast editorial typography.
      fontSize: {
        display: [
          "clamp(2.5rem, 1.5rem + 4.5vw, 4.75rem)",
          { lineHeight: "1.08", letterSpacing: "-0.015em", fontWeight: "600" },
        ],
        title: [
          "clamp(1.75rem, 1.2rem + 2.2vw, 2.75rem)",
          { lineHeight: "1.2", letterSpacing: "-0.01em", fontWeight: "600" },
        ],
      },

      borderRadius: {
        DEFAULT: "8px",
        lg: "12px",
      },

      boxShadow: {
        glow: "0 0 0 1px rgb(var(--accent) / 0.35), 0 8px 32px -8px rgb(var(--accent) / 0.55)",
        "glow-lg": "0 0 0 1px rgb(var(--accent) / 0.5), 0 12px 48px -8px rgb(var(--accent) / 0.7)",
        // Top inner highlight + soft drop: gives cards a sense of layered depth on dark backgrounds.
        card: "inset 0 1px 0 0 rgb(255 255 255 / 0.04), 0 8px 24px -12px rgb(0 0 0 / 0.6)",
      },

      backgroundImage: {
        "gradient-accent": "linear-gradient(135deg, rgb(var(--accent)) 0%, rgb(var(--accent-alt)) 100%)",
        // Palindrome (A > B > A) so the shimmer can ping-pong with no visible seam.
        "gradient-text": "linear-gradient(90deg, rgb(var(--accent)), rgb(var(--accent-alt)), rgb(var(--accent)))",
      },

      // Ambient, looping motion only. It runs on the compositor with zero JS.
      // Entrances and state-driven motion belong to the `motion` library in components.
      keyframes: {
        float: {
          "0%, 100%": { transform: "translateY(0)" },
          "50%": { transform: "translateY(-10px)" },
        },
        marquee: {
          from: { transform: "translateX(0)" },
          to: { transform: "translateX(-50%)" },
        },
        shimmer: {
          from: { backgroundPosition: "0% 50%" },
          to: { backgroundPosition: "100% 50%" },
        },
        drift: {
          from: { transform: "translate3d(0, 0, 0) scale(1)" },
          to: { transform: "translate3d(4%, -6%, 0) scale(1.12)" },
        },
      },
      animation: {
        float: "float 6s ease-in-out infinite",
        marquee: "marquee 40s linear infinite",
        shimmer: "shimmer 6s ease-in-out infinite alternate",
        drift: "drift 18s ease-in-out infinite alternate",
      },
    },
  },
};