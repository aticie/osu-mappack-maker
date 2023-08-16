/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        "surface": {
          DEFAULT: "#181212",
          on: "#d0c4c4",
          inverse: "#ece0e0",
          "inverse-on": "#201a1a"
        },
        "outline": {
          DEFAULT: "#9f8c8d"
        },
        "surface-container": {
          DEFAULT: "#241e1e",
          highest: "#3a3333"
        },
        "primary": {
          DEFAULT: "#ffb2ba",
          on: "#670020"
        },
        "primary-container": {
          DEFAULT: "#910130",
          on: "#ffd9dc"
        }
      }
    },
  },
  plugins: [],
}

