import { writable } from 'svelte/store';

// Create a writable store for CSRF token
export const csrfToken = writable<string | null>(null);

// Function to set CSRF token
export const setCsrfToken = (token: string) => {
  csrfToken.set(token);
};
