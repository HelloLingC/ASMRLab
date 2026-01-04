/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#42b983',
          hover: '#35a372',
          light: '#f0f8f5',
        },
        transcription: {
          DEFAULT: '#007bff',
          hover: '#0056b3',
          light: '#f0f8ff',
          border: '#b3d9ff',
        },
        destructive: {
          DEFAULT: '#ff6b6b',
          hover: '#ee5a5a',
        },
        success: {
          DEFAULT: '#28a745',
          hover: '#218838',
        },
      },
    },
  },
  plugins: [],
}

