/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}'],
  theme: {
    extend: {
      colors: {
        "paper": "#ffffff",
        "slateink": "#1e293b",
        "amber": "#b45309",
        "amberbg": "#fef3c7"
},
      fontFamily: {
        "display": [
                "'Newsreader'",
                "Georgia",
                "serif"
        ],
        "body": [
                "'Inter'",
                "system-ui",
                "sans-serif"
        ],
        "mono": [
                "'JetBrains Mono'",
                "ui-monospace",
                "monospace"
        ]
},
    },
  },
  plugins: [],
};
