<script lang="ts">
    import { goto } from '$app/navigation';
    import { onMount } from 'svelte';
  
    // Redirect to the home page when the component is mounted
    onMount(() => {
      goto('/home');
    });
  </script>
  