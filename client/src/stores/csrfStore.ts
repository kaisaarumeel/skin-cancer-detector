import { writable } from 'svelte/store';

// Create a writable store for CSRF token
export const csrfToken = writable<string | null>(null);