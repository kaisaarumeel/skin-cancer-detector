// Contributors:
// * Contributor: <alexandersafstrom@proton.me>
// * Contributor: <rokanas@student.chalmers.se>
import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
	plugins: [sveltekit()],
	define: {
		'process.env': {},
	  },
});
