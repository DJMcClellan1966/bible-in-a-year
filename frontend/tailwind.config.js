/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'bible-brown': '#8B4513',
        'bible-gold': '#DAA520',
        'saint-blue': '#4169E1',
        'divine-purple': '#8A2BE2',
        'grace-pink': '#FFB6C1',
      },
      fontFamily: {
        'serif': ['Georgia', 'Cambria', 'Times New Roman', 'serif'],
        'scripture': ['Times New Roman', 'serif'],
      },
    },
  },
  plugins: [],
}