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
  
    <div class="h-full w-full p-10 flex flex-col items-center justify-center">
        <h1 class="text-secondary text-3xl font-extralight mb-20">Results</h1>
        <p class="text-tertiary mb-10">Based on your uploaded image, it is likely that your mole is malignant.</p>
        <div class="p-8 h-20 bg-slate-50 flex items-center justify-center shadow-lg"> Model's prediction: 85% malignant.</div>
        <p class="text-tertiary mt-10"> With this prediction rate we advise your to go to a doctor to get a medical checkup on your mole.</p>
        <p class="text-tertiary text-sm font-extralight mt-10">Do you want to scan another mole?</p>
        <button on:click={reScan} class="w-1/2 p-3 bg-primary text-white font-light rounded-md cursor-pointer mt-1 transition-colors hover:bg-secondary shadow-l">Another scan</button>
    </div>
  </div>
  