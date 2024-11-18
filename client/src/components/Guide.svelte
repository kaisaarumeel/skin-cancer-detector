<script>
    import { createEventDispatcher } from 'svelte';
    
    // Create an event dispatcher to notify the parent component
    const dispatch = createEventDispatcher();

    export let currentStep = 1;

    const steps = [
      { title: "Step 1", description: "Upload only photos of moles." },
      { title: "Step 2", description: "Make sure the image is perpendicular to the mole." },
      { title: "Step 3", description: "Have only skin be visible in the photo." },
      { title: "Step 4", description: "Make sure the image has good lighting and is clearly focused on the mole." },
    ];
    
    function nextStep() {
        // Notify the parent to increment the step
        dispatch('nextStep'); 
    }
  </script>
    

<div class="bg-white opacity-95 rounded-lg p-8 shadow-md w-3/4 lg:w-2/4 h-1/2 flex flex-col justify-between items-center">
    <h2 class="text-2xl text-secondary font-light mb-4">{steps[currentStep - 1].title}</h2>
    <p class="text-tertiary">{steps[currentStep - 1].description}</p>

    <div class="flex justify-center items-center">
    <button
        on:click={nextStep}
        class="text-2xl font-bold text-gray-500 hover:text-gray-700">
        →
    </button>
    </div>

    <div class="flex items-center justify-center mt-6">
        {#each steps as _, index}
          <div class="flex items-center">
            <!-- Dot -->
            <div
              class={`h-4 w-4 rounded-full ${
                index + 1 <= currentStep ? "bg-primary" : "bg-gray-300"
              }`}
            ></div>
            
            <!-- Horizontal Line -->
            {#if index < steps.length - 1} <!-- Don't add a line after the last dot -->
              <div class="w-6 h-0.5 bg-gray-300 mx-2"></div>
            {/if}
          </div>
        {/each}
      </div>
</div>
