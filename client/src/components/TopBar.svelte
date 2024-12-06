<script>
    import { goto } from '$app/navigation';
    import { API } from '../api'; 


    async function handleLogout() {
      try {
        const response = await API.post('api/logout/');
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