<script lang="ts">
  import TopBar from "../../components/TopBar.svelte";
  import Guide from "../../components/Guide.svelte";
  import { goto } from '$app/navigation';
  import { routeGuard } from '../../routeGuard';  // Import the route guard
  import { onMount } from "svelte";
  import { API } from '../../api'; // Import the API instance
  import { isAxiosError } from "axios";

  // Check if the user is logged in when the page is loaded
  onMount(() => {
    routeGuard();
  });
    
  // Track the current step and visibility of the guide
  let currentStep = 1;
  const totalSteps = 5; // Updated to match the number of steps in Guide

  function nextStep() {
    if (currentStep < totalSteps) {
      currentStep++; // Increment currentStep
    }
  }

  let selectedFile: File | null = null;
  let fileName = "No file chosen";
  let localization = "";
  let errorMessage = "";


  // Check if a file is an acceptable image type (PNG, JPG, or JPEG)
  async function isValidImageType(file: File): Promise<string> {
    // Valid image file types
    const validTypes = ['image/png', 'image/jpeg', 'image/jpg'];

    // Reject if file is not of a valid format, else resolve
    return new Promise((resolve, reject) => {
      if (!validTypes.includes(file.type)) {
        reject("Invalid file type. Please upload a PNG, JPG, or JPEG image.");
      } else {
        resolve("");
      }
    });
  }

  // Function to handle the upload file event (via file input or drag-and-drop)
  async function handleFileChange(event: Event) {
    const input = event.target as HTMLInputElement; // Type assertion
    const file = input.files?.[0] || null;

    if (!file) {
      fileName = "No file chosen";
      errorMessage = "Please upload an image file of type JPG, JPEG, PNG."
      return;
    }
    
    // Check that the file is an acceptable image type
    try {
      const result = await isValidImageType(file);
      selectedFile = file;
      fileName = selectedFile.name;
      errorMessage = result;

    } catch (error) {
      selectedFile = null;
      fileName = "No file chosen";
      errorMessage = error as string;
    }
  }

  // Handle drag over event (prevents default behavior)
  function handleDragOver(event: DragEvent) {
    event.preventDefault();
  }

  // Handle drop event
  async function handleDrop(event: DragEvent) {
    event.preventDefault();
    const files = event.dataTransfer?.files;
    if (files && files.length > 0) {
      const file = files[0];
      
      // Check that the file is an acceptable image type
      try {
        const result = await isValidImageType(file);
        selectedFile = file;
        fileName = selectedFile.name;
        errorMessage = result;

      } catch (error) {
        selectedFile = null;
        fileName = "No file chosen";
        errorMessage = error as string;
      }
    }
  }


  // Function to handle analyze button click
  async function handleAnalyze(event: Event) {
    if (!selectedFile) {
      console.error("No file selected");
      errorMessage = "No file is selected.";
      return;
    }
    if (!localization) {
      console.error("No localization selected");
      errorMessage = "No localization is selected.";
      return;
    }
    
    try {
      const base64Image = await fileToBase64(selectedFile); // convert image to the base64 format
      const response = await API.post('/api/create-request/', {
        "localization": localization,
        "image": base64Image
      });

      if (response.status === 201) {
        const requestId = response.data?.request_id; 
        if (requestId) {
          goto(`/results/${requestId}`); // Navigate to the results page with the request ID
        } else {
          console.error("Request ID is missing from the response.");
        }
      }
    } catch(error) {
      // Check if the error was from server or network
      if (isAxiosError(error)) {
        // Safely access the data field and assert its type
        const errorResponse = error.response?.data as { err?: string } | undefined;
        // Check if the "err" property exists and is a string
        if (typeof errorResponse?.err === "string") {
          // Use it as error message
          errorMessage = errorResponse.err;
        } else {
          // Unknown error
          errorMessage = "An unknown server error occured.";
        }
      }
      console.error(error)
    }
  }

  function fileToBase64(file: File): Promise<string> {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();

      reader.onload = () => {
        const result = reader.result;
        if (typeof result === "string") {
          resolve(result.split(",")[1]); // Remove the base64 header
        } else {
          reject(new Error("Unexpected result type from FileReader"));
        }
      };

      reader.onerror = (error) => reject(error);
      reader.readAsDataURL(file); // Reads the file as a Base64 encoded string
    });
  }
</script>

<div class="h-screen flex flex-col relative">
  <TopBar></TopBar>

  <!-- Guide Component as an Overlay -->
  {#if currentStep < totalSteps}
    <div class="backdrop-blur-sm absolute top-0 left-0 w-full h-full bg-opacity-50 flex items-center justify-center">
      <Guide {currentStep} on:nextStep={nextStep}></Guide>
    </div>
  {/if}

  <div class="h-full w-full flex items-center justify-center">
    <div class="flex flex-col items-center justify-center lg:w-6/12 w-10/12">
      <h1 class="text-secondary text-3xl font-extralight mb-20">Upload a photo of your skin</h1>
      <p class="text-tertiary mb-2">For a more precise analysis choose the body part where the lesion is located.</p>

      <div class="mb-4 w-full">
        <select bind:value={localization} class="w-full p-2 border border-gray-300 rounded-md outline-none mt-1 focus:border-secondary text-gray-500 focus:text-black" aria-label="Body Part">
          <option value="" disabled selected class="text-gray-400">Select Body Part</option>
          <option value="ear">Ear</option>
          <option value="face">Face</option>
          <option value="neck">Neck</option>
          <option value="scalp">Scalp</option>
        
          <optgroup label="Trunk region">
            <option value="abdomen">Abdomen</option>
            <option value="back">Back</option>
            <option value="chest">Chest</option>
            <option value="trunk">Trunk - Other</option>
          </optgroup>
        
          <optgroup label="Upper limbs">
            <option value="acral">Acral (Fingers/Toes)</option>
            <option value="hand">Hand</option>
            <option value="upper extremity">Upper Extremity (Arm)</option>
          </optgroup>
        
          <optgroup label="Lower limbs">
            <option value="foot">Foot</option>
            <option value="lower extremity">Lower Extremity (Leg)</option>
          </optgroup>
        
          <option value="genital">Genital Area</option>
        </select>
      </div>

      <form class="mt-10 w-full">
        <!-- Drop area for drag and drop -->
        <!-- svelte-ignore a11y_no_static_element_interactions -->
        <div 
          class="flex items-center bg-slate-50 shadow-md p-3 rounded-lg justify-between"
          on:dragover={handleDragOver} 
          on:drop={handleDrop} 
          style="min-height: 150px; border: 2px dashed #ccc; justify-content: center; cursor: pointer;">
          
          <label for="fileInput" class="p-2 border-tertiary border rounded-2xl flex items-center text-tertiary font-light cursor-pointer mr-4 hover:bg-stone-200">
            <img src="upload-file.png" alt="Upload a File" class="h-5 mr-4">
            Upload File
          </label>
          
          <input
            id="fileInput"
            type="file"
            class="hidden"
            accept=".png, .jpg, .jpeg"
            on:change={handleFileChange}
          />
          
          <span class="text-tertiary">{fileName}</span>
        </div>
      </form>

      <button on:click={handleAnalyze} class="w-1/2 p-3 bg-primary text-white font-light rounded-md cursor-pointer mt-10 hover:bg-secondary shadow-l">Analyze</button>

      {#if errorMessage}
        <p class="text-red-500 text-sm mt-2 ">{errorMessage}</p>
      {/if}
    </div>
  </div>
</div>
