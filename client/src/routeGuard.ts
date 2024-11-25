import { API } from "./api";
import { goto } from '$app/navigation';

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

