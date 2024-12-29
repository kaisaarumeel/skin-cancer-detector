// Contributors:
// * Contributor: <alexandersafstrom@proton.me>
// * Contributor: <kaisa.arumeel@gmail.com>
import type { Config } from 'tailwindcss';

export default {
  content: ['./src/**/*.{html,js,svelte,ts}'],

  theme: {
    extend: {
      colors: {
        primary: '#B7A9D4',   // Lighter purple
        secondary: '#7C64AD', // Darker purple
        tertiary: '#626262',  // Brown used for text
      },
    },
  },

  plugins: []
} satisfies Config;
