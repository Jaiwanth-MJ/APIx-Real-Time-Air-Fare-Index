/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        navy: {
          950: '#060D17',
          900: '#0D1B2A',
          800: '#14253B',
          700: '#1B314D',
        },
        surface: {
          card: '#16283D',
          hover: '#1D344F',
          border: '#223F5E'
        },
        brand: {
          teal: '#00C9A7',
          tealDim: '#00A387',
          cyan: '#00E5FF',
          orange: '#FF9F43',
          red: '#FF5252',
          blue: '#4D96FF'
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      }
    },
  },
  plugins: [],
}
