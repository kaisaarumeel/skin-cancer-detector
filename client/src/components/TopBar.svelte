<script>
// Contributors:
// * Contributor: <kaisa.arumeel@gmail.com>
// * Contributor: <rokanas@student.chalmers.se>

    import { goto } from '$app/navigation';
    import { API } from '../api'; 
    import { getCSRFToken } from '../stores/csrfStore'; // Import CSRF token


    async function handleLogout() {
      try {
        const response = await API.post('api/logout/', {}, {
          headers: {
            'X-CSRFToken': getCSRFToken(),
          }
        });
        if (response.status === 200) {
          console.log('User logged out successfully');
         goto('/home');
        }
      } catch (err) {
        console.error('Error logging out:', err);
      }
    }

    async function getScans() {
         goto('/scans');
    }
</script>

<div class="shadow h-16 w-full bg-primary flex items-center justify-end pr-20 font-light text-white"> 
    <button class="mr-8" on:click={getScans}>My scan history</button>   
    <button on:click={handleLogout}>Log out</button>
</div>