/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}'],
  theme: {
    extend: {
      colors: {
        // ContraLens dossier palette
        paper: '#f1efe8',
        newsprint: '#f1efe8',
        panel: '#faf8f2',
        rules: '#cfc9bd',
        ink: '#181818',
        soft: '#5f5b54',
        signal: '#b3261e',
        slateink: '#181818',
        // Legacy names still used by the React islands
        amber: '#b3261e',
        amberbg: '#f3deda',
        slate: {
          50: '#f6f3eb',
          100: '#efede4',
          200: '#ddd7ca',
          300: '#cfc9bd',
          400: '#a49e92',
          500: '#7a746a',
          600: '#5f5b54',
          700: '#3b3934',
          800: '#242321',
          900: '#181818',
        },
        red: {
          50: '#fbf0ee',
          100: '#f2d9d5',
          200: '#e5b4ac',
          300: '#d68a7f',
          400: '#c55c4f',
          500: '#b3261e',
          600: '#991f19',
          700: '#7c1914',
          800: '#63140f',
          900: '#4a100c',
        },
      },
      fontFamily: {
        display: ["'Libre Caslon Display'", 'Georgia', 'serif'],
        body: ["'Public Sans'", 'system-ui', 'sans-serif'],
        mono: ["'Space Mono'", 'ui-monospace', 'monospace'],
      },
    },
  },
  plugins: [],
};
