// Contributors:
// * Contributor: <kaisa.arumeel@gmail.com>
import { API } from "./api";
import { goto } from '$app/navigation';
import type { AxiosError } from 'axios';

export async function routeGuard(adminCheck = false) {
    try {
        // Make API call to check if the user is logged in
        const response = await API.get('api/is_logged_in/');
        if (!response.data.is_logged_in) {
            console.log('User is not logged in, redirecting to home...');
            goto('/'); 
            return;
        }

        // If admin check is passed in as true
        if (adminCheck) {
            const adminResponse = await API.get('api/is_admin/');
            if (!adminResponse.data.is_admin) {
                console.log('User is not an admin, redirecting to home...');
                goto('/'); 
            }
        }
    } catch (err) {
        console.error('Error checking status:', err);
        goto('/'); 
    }
}

// Prevent repeated checks
let isChecked = false; 

export async function loggedInRedirect() {
    if (isChecked) return; // Avoid redundant API calls
    try {
        const response = await API.get('api/is_logged_in/');
        if (response.data.is_logged_in) {
            // Check if the user is an admin
            const adminResponse = await API.get('api/is_admin/');
            if (adminResponse.data.is_admin) {
                // If user is admin, redirect to /admin page
                goto('/admin');
            } else {
                // Otherwise, redirect to /upload page
                goto('/upload');
            }
        }
    } catch (err: unknown) {
        if ((err as AxiosError).isAxiosError) {
            const axiosError = err as AxiosError;
            if (axiosError.response?.status !== 401) {
                console.error('Unexpected error while checking login status:', axiosError.message);
            }
        } else {
            console.error('Unknown error occurred:', err);
        }
    } finally {
        isChecked = true; // Ensure the check happens only once
    }
}
