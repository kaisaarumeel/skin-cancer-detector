// Contributors:
// * Contributor: <elindstr@student.chalmers.se>
// * Contributor: <rokanas@student.chalmers.se>
import { API } from '../api'; // Import the API instance

// function to generate CSRF token, set to browser cookies and return it
export async function generateCSRFToken() {
  try {
    const response = await API.get('/api/get-csrf-token/');
    console.log(response)
  } catch (error) {
    console.error("Error fetching CSRF token:", error);
  }
}

export function getCSRFToken() {
    // Check if the cookie exists in the browser storage
    // If it exists, return it
    const csrfCookie = document.cookie
      .split('; ')
      .find(row => row.startsWith('csrftoken='));
    return csrfCookie ? csrfCookie.split('=')[1] : null;
}
