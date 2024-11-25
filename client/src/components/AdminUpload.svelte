<script lang="ts">
   let isDragging: boolean = false; // State to indicate drag-and-drop activity
    let uploadedFile: File | null = null; // State to hold the uploaded file, initially null
    let submitEnabled: boolean = false; // Submit button visibility

    const handleDrop = (event: DragEvent) => {
      event.preventDefault();
      event.stopPropagation();
      isDragging = false;
  
      if (event.dataTransfer?.files && event.dataTransfer.files.length > 0) {
        const file = event.dataTransfer.files[0];
        if (file.type === "application/zip") {
          uploadedFile = file;
          submitEnabled = true; // Enable submit button after file upload
        } else {
          alert("Please upload a .zip file.");
        }
      }
    };
  
    const handleDragOver = (event: DragEvent) => {
      event.preventDefault();
      isDragging = true;
    };
  
    const handleDragLeave = () => {
      isDragging = false;
    };
  
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Enter" || event.key === " ") {
        document.getElementById("fileUpload")?.click();
      }
    };
  
    const handleFileSelect = (event: Event) => {
      const target = event.target as HTMLInputElement;
      const file = target.files?.[0];
      if (file && file.type === "application/zip") {
        uploadedFile = file;
        submitEnabled = true; // Enable submit button after file upload
      } else {
        alert("Please upload a .zip file.");
      }
    };
  
    const handleSubmit = () => {
      if (uploadedFile) {
        alert(`File ${uploadedFile.name} has been submitted successfully!`);
        // Logic to handle file submission goes here
        uploadedFile = null;
        submitEnabled = false; // Reset after submission
      }
    };

</script>

<div class="bg-white rounded-lg shadow-md p-4 flex flex-col items-start relative">
    <h2 class="text-lg font-regular text-secondary">Upload New Training Data</h2>
    <p class="text-sm text-tertiary mt-2">Drag and drop a .zip file or use the button below to upload new training data.</p>

    <div
      role="button"
      aria-label="File upload drop zone"
      tabindex="0"
      class={`mt-4 w-full h-full min-h-40 border-2 ${
        isDragging ? "border-secondary bg-primary" : "border-gray-300 bg-gray-50"
      } rounded-md flex items-center justify-center text-tertiary`}
      on:dragover={handleDragOver}
      on:dragleave={handleDragLeave}
      on:drop={handleDrop}
      on:keydown={handleKeyDown}
    >
      {#if uploadedFile}
        <p class="text-sm text-tertiary">Uploaded: {uploadedFile.name}</p>
      {:else}
        <p class="text-sm text-tertiary">Drag and drop a .zip file here</p>
      {/if}
    </div>

    <label
      class="mt-4 w-full py-2 px-4 bg-primary text-white rounded-md text-center cursor-pointer hover:bg-secondary"
      for="fileUpload"
    >
      {uploadedFile ? "Replace File" : "Upload File"}
    </label>
    <input
      id="fileUpload"
      type="file"
      accept=".zip"
      class="hidden"
      on:change={handleFileSelect}
    />

    {#if submitEnabled}
      <button
        class="mt-4 w-full py-2 px-4 bg-primary text-white rounded-md hover:bg-secondary"
        on:click={handleSubmit}
      >
        Submit
      </button>
    {/if}
  </div>