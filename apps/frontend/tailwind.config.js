/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#0A0A0B",
        surface: {
          DEFAULT: "#141416",
          hover: "#1C1C1F",
        },
        border: {
          DEFAULT: "rgba(255,255,255,0.08)",
          strong: "rgba(255,255,255,0.14)",
        },
        text: {
          primary: "#F5F5F5",
          secondary: "#A1A1AA",
          muted: "#71717A",
        },
        accent: {
          DEFAULT: "#6366F1",
          hover: "#7C7FF2",
          muted: "#6366F11A",
        },
        success: { DEFAULT: "#10B981", muted: "#10B9811A" },
        warning: { DEFAULT: "#F59E0B", muted: "#F59E0B1A" },
        error:   { DEFAULT: "#EF4444", muted: "#EF44441A" },
        info:    { DEFAULT: "#3B82F6", muted: "#3B82F61A" },
      },
      fontFamily: {
        sans: ["Inter", "Geist", "sans-serif"],
      },
      borderRadius: {
        DEFAULT: "8px",
        lg: "12px",
      },
    },
  },
};
