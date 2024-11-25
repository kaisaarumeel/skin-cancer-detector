<script>
    function retrain() {
      // Add retrain logic here
      console.log("Retrain")
    }
</script>

<div class="bg-white rounded-lg shadow-md p-4 flex flex-col items-start justify-between">
          <h2 class="text-lg font-regular text-secondary">Retrain Model</h2>
          <p class="text-sm text-tertiary mt-2">Click on the button below to retrain the model.</p>
          <button
          class="mt-4 w-full py-2 px-4 bg-primary text-white rounded-md hover:bg-secondary"
          on:click={retrain}>
          Retrain Model
        </button>
</div>