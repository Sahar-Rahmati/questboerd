/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          ink: "#132A2E",
          lagoon: "#1C6E72",
          mint: "#CDEAE5",
          sand: "#F4EBD0",
          ember: "#E76F51",
          gold: "#D8A31A",
        },
      },
      boxShadow: {
        panel: "0 18px 50px rgba(19, 42, 46, 0.08)",
      },
      fontFamily: {
        sans: ["'Manrope'", "ui-sans-serif", "system-ui"],
      },
      backgroundImage: {
        hero: "radial-gradient(circle at top left, rgba(205,234,229,0.9), transparent 42%), linear-gradient(135deg, #fdfbf5 0%, #f4ebd0 48%, #ffffff 100%)",
      },
    },
  },
  plugins: [],
};
