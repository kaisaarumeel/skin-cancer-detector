import { writable } from 'svelte/store';

export function getCSRFToken() {
    // Check if the cookie exists in the browser storage
    // If it exists, return it
    const csrfCookie = document.cookie
      .split('; ')
      .find(row => row.startsWith('csrftoken='));
    return csrfCookie ? csrfCookie.split('=')[1] : null;
}
