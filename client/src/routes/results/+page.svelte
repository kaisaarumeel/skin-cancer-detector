<script>
    import TopBar from "../../components/TopBar.svelte";
    import { goto } from '$app/navigation';

    function reScan() {
    // Add sign in endpoint/logic here
    goto('/upload');
  }
  </script>
    
  <div class="h-screen flex flex-col relative">
    <TopBar></TopBar>
  
    <div class="h-full w-full flex flex-col items-center justify-center">
        <h1 class="text-secondary text-3xl font-extralight mb-20">Results</h1>
        <p class="text-tertiary mb-2">Results here.</p>
        <button on:click={reScan} class="w-1/2 p-3 bg-primary text-white font-light rounded-md cursor-pointer mt-10 transition-colors hover:bg-secondary shadow-l">Another scan</button>
    </div>
  </div>
  