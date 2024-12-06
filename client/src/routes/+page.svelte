<script lang="ts">
    import { goto } from '$app/navigation';
    import { onMount } from 'svelte';
    import { getCsrfTokenFromBrowser } from '../stores/csrfStore'; 
  
    // Redirect to the home page when the component is mounted
    onMount(() => {
      getCsrfTokenFromBrowser();
      goto('/home');
    });
  </script>
  