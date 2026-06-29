/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        uipath: {
          orange: '#FA4616',
          dark: '#000000',
          darker: '#111111',
          gray: '#2C2C2C',
        }
      }
    },
  },
  plugins: [],
}
