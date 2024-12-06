import { writable } from 'svelte/store';

// Create a writable store for CSRF token
export const csrfToken = writable<string | null>(null);

export function getCsrfTokenFromBrowser() {
    // Check if the cookie exists in the browser storage
    // If it exists, add it to the store
    const csrfCookie = document.cookie
      .split('; ')
      .find(row => row.startsWith('csrftoken='));
    if (csrfCookie) csrfToken.set(csrfCookie.split('=')[1]);
}
