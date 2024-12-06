<script lang="ts">
  import { API } from "../api";
  import type { AxiosResponse, AxiosError } from "axios";
  import { csrfToken } from '../stores/csrfStore'; // Import CSRF token

  let isDragging: boolean = false; // State to indicate drag-and-drop activity
  let uploadedFile: File | null = null; // State to hold the uploaded file, initially null
  let submitEnabled: boolean = false; // Submit button visibility
  let message: string = ""; // Stores response message
  let isSubmitted: boolean = false; // State to indicate submission 
  let isError: boolean = false // State to indicate error with submission

  const handleDrop = (event: DragEvent) => {
    event.preventDefault();
    event.stopPropagation();
    isDragging = false;

    if (event.dataTransfer?.files && event.dataTransfer.files.length > 0) {
      const file = event.dataTransfer.files[0];
      const fileExtension = file.name.split('.').pop()?.toLowerCase();
      if (fileExtension === "zip") {
        uploadedFile = file;
        submitEnabled = true; // Enable submit button after file upload
        isError = false;
      } else {
        isError = true;
        message = "Please upload a valid .zip file";
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

    if (file) { 
      const fileExtension = file.name.split('.').pop()?.toLowerCase(); 

      if (fileExtension === "zip") { 
        uploadedFile = file;
        submitEnabled = true;
        isError = false;
      } else {
        isError = true;
        message = "Please upload a valid .zip file";
      }
    } else {
      isError = true;
      message = "No file selected. Please try again.";
    }
    target.value = ""; // reset input value
  };

  const handleSubmit = async () => {
    if (uploadedFile) {
      const formData = new FormData();
      formData.append("file", uploadedFile);

      try {
        const response = await API.post("/api/add-data/", formData, {
          headers: {
            "Content-Type": "multipart/form-data",
            'X-CSRFToken': $csrfToken,
          },
        });
        message = response.data.message;
        isError = false;
        
      } catch (error) {
        const axiosError = error as AxiosError<{ err: string }>;
        if (axiosError.response) {
          message = axiosError.response.data.err
          isError = true;
        }
      }
      console.log(message);
      isSubmitted = true;
      uploadedFile = null;
      submitEnabled = false; // reset after submission
    }
  };

</script>

<div class="bg-white rounded-lg shadow-md p-4 flex flex-col items-start relative">
  <h2 class="text-lg font-regular text-secondary">Upload New Training Data</h2>
  <p class="text-sm text-tertiary mt-2">Drag and drop a .zip file or use the button below to upload new training data. 
    Zip file must contain "metadata.cv" and an "images" folder.</p>

  <div
    role="button"
    aria-label="File upload drop zone"
    tabindex="0"
    class={`mt-4 w-full h-full min-h-40 border-2 ${
      isDragging ? "border-secondary bg-primary" : "border-gray-300 bg-gray-50"
    } rounded-md flex flex-col items-center justify-center text-tertiary`}
    on:dragover={handleDragOver}
    on:dragleave={handleDragLeave}
    on:drop={handleDrop}
    on:keydown={handleKeyDown}
  >
    {#if uploadedFile && isError}
      <p class="text-sm text-tertiary">Uploaded: {uploadedFile.name}</p>
      <p class="text-sm text-red-600">{message}</p>
    {:else if uploadedFile}
      <p class="text-sm text-tertiary">Uploaded: {uploadedFile.name}</p>
    {:else if isError}
      <p class="text-sm text-red-600">{message}</p>
    {:else if isSubmitted}
      <p class="text-sm text-green-600">{message}</p>
    {:else}
      <p class="text-sm text-tertiary">Drag and drop a .zip file here</p>
    {/if}
  </div>

  <label
    class="mt-4 w-full py-2 px-4 bg-primary text-white rounded-md text-center cursor-pointer hover:bg-secondary"
    for="fileUpload"
  >
    {#if uploadedFile}
      {"Replace File"}
    {:else if isSubmitted}
      {"Upload Another File"}
    {:else}
      {"Upload File"}
    {/if}
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