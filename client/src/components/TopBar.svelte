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
</script>

<div class="shadow h-16 w-full bg-primary flex flex-col items-end justify-center pr-20 font-light text-white">    
    <button on:click={handleLogout}>Log out</button>
</div>