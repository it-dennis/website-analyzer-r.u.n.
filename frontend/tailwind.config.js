/** Farben und Typografie nach dem R.U.N.-Markenbuch (Nocturne): Nachtblau-Grund, ein violetter Akzent, Inter. */
/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        bg: '#161826',
        surface: '#232532',
        ink: '#e9e9ed',
        line: 'rgba(233, 233, 237, 0.14)',
        neutral: {
          100: '#f3f5fe', 200: '#e4e7f5', 300: '#cfd3e5', 400: '#b2b6ca', 500: '#9397ab',
          600: '#75798c', 700: '#595d6c', 800: '#3f424d', 900: '#292b31',
        },
        accent: {
          DEFAULT: '#9184d9',
          100: '#f5f4ff', 200: '#e7e5fe', 300: '#d2cefd', 400: '#b5abfc', 500: '#968ae0',
          600: '#796cbf', 700: '#5d5294', 800: '#423a6a', 900: '#2b2741',
        },
        // Statusfarben: gedämpft, damit der Akzent die einzige gesättigte Farbe der Oberfläche bleibt.
        good: '#7ccf9a',
        warn: '#e6bd6f',
        bad: '#ee8a8a',
      },
      fontFamily: {
        sans: ['"Inter Variable"', 'Inter', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        card: '0 1px 0 rgba(233,233,237,0.04) inset, 0 8px 24px -12px rgba(0,0,0,0.5)',
      },
    },
  },
  plugins: [],
}
