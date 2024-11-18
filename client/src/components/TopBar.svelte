<script>
    import { goto } from '$app/navigation';
  
    function handleLogout() {
    // Add logout endpoint/logic here
      goto('/home');
    }
</script>

<div class="h-16 w-full bg-primary flex flex-col items-end justify-center pr-20 font-light text-white">    
    <button on:click={handleLogout}>Log out</button>
</div>