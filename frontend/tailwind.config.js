/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'alive-dark': '#1A1A1A',
        'alive-button': '#2D2D2D',
        'alive-hover': '#404040',
        'alive-active': '#FF4444',
      },
    },
  },
  plugins: [],
}

