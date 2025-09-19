/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: ['./index.html', './src/**/*.{svelte,js}'],
  theme: {
    extend: {
      container: { center: true, padding: '1rem' },
      borderRadius: { '2xl': '1rem' }
    },
  },
  plugins: [require('@tailwindcss/forms'), require('@tailwindcss/typography')],
}
